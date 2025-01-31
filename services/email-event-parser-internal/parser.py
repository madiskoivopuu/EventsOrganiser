from helpers.email_data import Email
from llm.model import Llama3Model 
from helpers import mq_email_parser

from dataclasses import dataclass
from collections.abc import Callable
from queue import Queue
import functools
import threading, json
import pika.spec


@dataclass
class ParseRequest:
    connection: pika.BlockingConnection
    channel: pika.spec.Basic.Deliver
    delivery_tag: int
    body: bytes

@dataclass
class ParseResponse:
    events: list[dict]
    user_id: str
    account_type: str
    mail_link: str

# This should still work fine with pika andmost LLM libraries, since 
# most of them release the GIL when it comes time to run the LLM with a prompt
class ParserThread(threading.Thread):
    def __init__(self, queue: Queue, llm_model_path: str, callback: Callable):
        super(ParserThread, self).__init__()

        self.callback = callback
        self.email_queue = queue
        self.current_work_delivery_tag = None
        self.llm = Llama3Model(llm_model_path)

    def run(self):
        while True:
            data: ParseRequest = self.email_queue.get()
            if(data == None):
                return

            self.current_work_delivery_tag = data.delivery_tag
            
            # TODO: add some proper error handling in case

            msg_with_email: dict[str] = json.loads(data.body)
            email: Email = mq_email_parser.parse(msg_with_email)
            events = self.parse_and_validate(email)

            callback_with_args = functools.partial(self.callback, data.channel, data.delivery_tag, ParseResponse(
                events=events["events"], # TODO: figure out why it's a dictionary not a list
                user_id=msg_with_email["user_id"],
                account_type=msg_with_email["account_type"],
                mail_link=email.mail_link
            ))

            data.connection.add_callback_threadsafe(callback_with_args)
            self.current_work_delivery_tag = None

    def parse_and_validate(self, email: Email) -> list[dict]:
        events = self.llm.parse_events_from_email(email)
        return events

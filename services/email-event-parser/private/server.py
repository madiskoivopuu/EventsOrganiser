import server_config
import parser
from parser import ParseResponse

import pika, pika.spec, pika.channel, json
import dataclasses
from queue import Queue

THREAD_CHECK_DELAY_SEC = 10

class EmailQueueServer():
    def __init__(self):
        self.queue = Queue()
        self.mq_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=server_config.RABBITMQ_HOST, 
                port=5672, 
                virtual_host=server_config.RABBITMQ_VIRTUALHOST, 
                credentials=pika.PlainCredentials(server_config.RABBITMQ_USERNAME, server_config.RABBITMQ_PASSWORD))
        )
        self.mq_channel = self.mq_connection.channel()
        self.parser_thread = parser.ParserThread(self.queue, server_config.LLM_PATH, self.email_parsed_callback)

    def check_parser_thread_status(self):
        """Periodically recheck that the required parser thread hasn't crashed
           Restarts the thread and NACK's the previous work item if there is an issue
        """
        if(not self.parser_thread.is_alive()):
            # TODO: some logging to mention that the thread is starting up again
            
            if(self.parser_thread.current_work_delivery_tag and self.mq_channel.is_open):
                self.mq_channel.basic_nack(self.parser_thread.current_work_delivery_tag)

            self.parser_thread = parser.ParserThread(self.queue, server_config.LLM_PATH, self.email_parsed_callback)
            self.parser_thread.start()

        self.mq_connection.call_later(THREAD_CHECK_DELAY_SEC, self.check_parser_thread_status)

    def email_parsed_callback(
            self, 
            channel: pika.channel.Channel, 
            delivery_tag: pika.spec.BasicProperties,
            response: ParseResponse):
        
        self.mq_channel.basic_publish(
            exchange="",
            routing_key=server_config.RABBITMQ_EVENTS_OUTPUT_QUEUE,
            body=json.dumps(dataclasses.asdict(response))
        )

        channel.basic_ack(delivery_tag)

    def on_new_email(self, channel: pika.channel.Channel, 
                    method: pika.spec.Basic.Deliver, 
                    properties: pika.spec.BasicProperties, 
                    body: bytes):
        
        request = parser.ParseRequest(
            self.mq_connection,
            channel,
            method.delivery_tag,
            body
        )
        self.queue.put(request)

    def run(self):
        self.mq_channel.queue_declare(server_config.RABBITMQ_EMAILS_QUEUE, durable=True)
        self.mq_channel.queue_declare(
            server_config.RABBITMQ_EVENTS_OUTPUT_QUEUE, 
            durable=True,
            arguments={
                'x-dead-letter-exchange': 'dlx', # Specify the DLQ exchange
                'x-dead-letter-routing-key': 'dead_events'      # Routing key for dead messages
            }
        )

        self.mq_channel.basic_consume(server_config.RABBITMQ_EMAILS_QUEUE, self.on_new_email)
        self.mq_channel.basic_qos(prefetch_count=1)

        try:
            self.parser_thread.start()
            self.mq_connection.call_later(THREAD_CHECK_DELAY_SEC, self.check_parser_thread_status)
            self.mq_channel.start_consuming()
        finally:
            self.mq_channel.stop_consuming()
            self.mq_connection.close()

            self.queue.put(None)
            self.parser_thread.join()

if __name__ == "__main__":
    queue_server = EmailQueueServer()
    queue_server.run()
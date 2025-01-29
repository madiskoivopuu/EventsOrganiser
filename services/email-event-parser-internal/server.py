import server_config
import parser

import pika, pika.spec, pika.channel
from queue import Queue

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
        """Make sure that the parser thread has not crashed, before sending the email over
        
        """
        if(not self.parser_thread.is_alive()):
            # TODO: some logging to mention that the thread is starting up again
            # maybe not the best idea to restart the thread each time?
            self.parser_thread = parser.ParserThread(self.queue, server_config.LLM_PATH, self.email_parsed_callback)
            self.parser_thread.start()

    def email_parsed_callback(self, channel: pika.spec.Basic.Deliver, 
                            delivery_tag: pika.spec.BasicProperties):
        pass

    def on_new_email(self, channel: pika.channel.Channel, 
                    method: pika.spec.Basic.Deliver, 
                    properties: pika.spec.BasicProperties, 
                    body: bytes):
        self.check_parser_thread_status()

        request = parser.ParseRequest(
            self.mq_connection,
            channel,
            method.delivery_tag,
            body
        )
        self.queue.put(request)

    def run(self):
        self.mq_channel.queue_declare(server_config.RABBITMQ_QUEUE, durable=True)
        self.mq_channel.basic_consume(server_config.RABBITMQ_QUEUE, self.on_new_email)

        try:
            self.parser_thread.start()
            self.mq_channel.start_consuming()
        finally:
            self.mq_channel.stop_consuming()
            self.mq_connection.close()

            self.queue.put(None)
            self.parser_thread.join()

if __name__ == "__main__":
    queue_server = EmailQueueServer()
    queue_server.run()
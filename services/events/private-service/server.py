import server_config
import validator
from validator import NewEvents, ParsedEvent


import pika, pika.spec, pika.channel
from datetime import datetime, timezone
import sqlalchemy.exc
import pydantic

import logging
logging.basicConfig(level=logging.INFO)

class EventsServer():
    def __init__(self):
        self.logger = logging.getLogger(__name__ + "." + type(self).__name__)
        self.mq_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=server_config.RABBITMQ_HOST, 
                port=5672, 
                virtual_host=server_config.RABBITMQ_VIRTUALHOST, 
                credentials=pika.PlainCredentials(server_config.RABBITMQ_USERNAME, server_config.RABBITMQ_PASSWORD))
        )
        self.mq_channel = self.mq_connection.channel()

    def _on_new_events(self, channel: pika.channel.Channel, 
                    method: pika.spec.Basic.Deliver, 
                    properties: pika.spec.BasicProperties, 
                    body: bytes):
        try:
            data: NewEvents = NewEvents.model_validate_json(body)
        except pydantic.ValidationError:
            self.logger.warning(f"Events from an email rejected due to data validation errors", exc_info=True)
            channel.basic_reject(method.delivery_tag, requeue=False)
            return
        
        try:
            validator.add_events_to_db(data)
            channel.basic_ack(method.delivery_tag)
        except ValueError:
            self.logger.warning("Unexpected ValueError when adding events to the database", exc_info=True)
            channel.basic_reject(method.delivery_tag, requeue=False)
        except sqlalchemy.exc.OperationalError:
            self.logger.error("Unable to execute queries on the events MySQL database", exc_info=True)
            channel.basic_reject(method.delivery_tag, requeue=True)
        except Exception:
            self.logger.error("Unknown exception occurred", exc_info=True)
            channel.basic_reject(method.delivery_tag, requeue=False)
            pass
        
    def _create_queues(self):
        self.mq_channel.exchange_declare(exchange='dlx', exchange_type='direct')
        self.mq_channel.queue_declare(queue='dead_events')
        self.mq_channel.queue_bind(queue='dead_events', exchange='dlx', routing_key='dead_events')

        self.mq_channel.queue_declare(
            server_config.RABBITMQ_EVENTS_OUTPUT_QUEUE, 
            durable=True,
            arguments={
                'x-dead-letter-exchange': 'dlx', # Specify the DLQ exchange
                'x-dead-letter-routing-key': 'dead_events'      # Routing key for dead messages
            }
        )

    def run(self):
        self._create_queues()

        self.mq_channel.basic_consume(server_config.RABBITMQ_EVENTS_OUTPUT_QUEUE, self._on_new_events)
        self.mq_channel.basic_qos(prefetch_count=1)

        try:
            self.mq_channel.start_consuming()
        finally:
            self.mq_channel.stop_consuming()
            self.mq_connection.close()

if __name__ == "__main__":
    server = EventsServer()
    server.run()
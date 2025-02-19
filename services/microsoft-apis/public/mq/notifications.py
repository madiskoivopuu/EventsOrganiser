import asyncio, json

from typing import Callable, Awaitable

import aio_pika

import logging


class NotifiactionMQ:
    def __init__(self, host: str, virtual_host: str, username: str, password: str, 
                 queue_name: str, routing_key: str, notification_callback: Callable[[dict], Awaitable[bool]]):
        """
        Creates an instance of a MQ client listening for notifications on 'queue_name' that are routed there with 'routing_key'

        :param host: IP of the broker
        :param virtual_host: Virtual host name
        :param username: Broker login username
        :param password: Broker login password
        :param routing_key: Defines which type of notifications in RabbitMQ to send to a queue defined by 'queue_name'
        :queue_name: Queue to receive certain notifications on
        :param notification_callback: An async function that gets called on a new notification. 
            The callback must take a dictionary and return a bool value (True indicating that the notification was successfully processed)
        """
        self.__logger = logging.getLogger(__name__)

        self._ioloop = asyncio.get_running_loop()
        self._mq_conn_coroutine = aio_pika.connect_robust(
            host=host,
            virtualhost=virtual_host,
            login=username,
            password=password
        )

        self.mq_connection = None
        self.mq_channel = None
        self.notification_exchange = None

        self.queue_name = queue_name
        self.routing_key = routing_key
        self.notification_callback = notification_callback

    async def open_conn(self) -> bool:
        self.mq_connection = await self._mq_conn_coroutine
        self.mq_channel = await self.mq_connection.channel()
        await self.mq_channel.set_qos(prefetch_count=10)

        self.notification_exchange = await self.mq_channel.declare_exchange(name="notifications", type=aio_pika.ExchangeType.TOPIC)
        queue = await self.mq_channel.declare_queue(
            name=self.queue_name,
            durable=True
        )
        await queue.bind(exchange="notifications", routing_key=self.routing_key)

        await queue.consume(self._on_notification)

        return self.mq_connection != None

    async def close_conn(self):
        if(not self.mq_connection.is_closed):
            await self.mq_connection.close()    

    async def send_notification(self, data: dict, routing_key: str, **kwargs):
        """
        Send a notification through 'notifications' exchange with a routing key

        :param data: Message content to send
        :param routing_key: AMQP routing key for the message
        :param kwargs: Extra arguments for aio_pika.Message
        """
        await self.notification_exchange.publish(
            aio_pika.Message(
                body=json.dumps(data).encode(),
                **kwargs
            ),
            routing_key=routing_key,
        )

    async def _on_notification(self, msg: aio_pika.message.AbstractIncomingMessage):
        try:
            data = json.loads(msg.body.decode())
        except json.JSONDecodeError:
            self.__logger.error("Unable to decode new user notification due to a programmer JSON formatting error", exc_info=True, stack_info=True)
            await msg.reject()

        try:
            proc_success = await self.notification_callback(data)
            if(proc_success):
                await msg.ack()
            else:
                self.__logger.warning(f"Notification was not processed fully by callback '{getattr(self.notification_callback, "__name__", repr(self.notification_callback))}'", exc_info=True)
                await msg.nack(requeue=True)
        except Exception:
            self.__logger.warning("Error passing on notification to 'notification_callback'", exc_info=True)
import asyncio, json
import sqlalchemy.exc
from sqlalchemy import select
from zoneinfo import ZoneInfo

import aio_pika

from common import tables

import db
import logging

class MailSenderMQ:
    def __init__(self, host: str, virtual_host: str, username: str, password: str, queue_name: str):
        self.__logger = logging.getLogger(__name__)

        self._ioloop = asyncio.get_running_loop()
        self._mq_conn_coroutine = aio_pika.connect_robust(
            host=host,
            virtualhost=virtual_host,
            username=username,
            password=password
        )

        self.mq_connection = None
        self.mq_channel = None
        self.queue_name = queue_name

    async def open_conn(self) -> bool:
        self.mq_connection = await self._mq_conn_coroutine
        self.mq_channel = await self.mq_connection.channel()

        await self.mq_channel.declare_queue(
            name=self.queue_name,
            durable=True
        )

        return self.mq_connection != None

    async def send_new_emails_to_parse(
        self,
        user_id: str,
        user_email: str,
        user_timezone: ZoneInfo,
        emails: list[dict[str]]
    ):
        async with self.mq_channel.transaction():
            for email in emails:
                self.mq_channel.default_exchange.publish(
                    message=aio_pika.Message(
                        body=json.dumps({
                            "user_id": user_id,
                            "account_type": "outlook",
                            "user_timezone": str(user_timezone),
                            "email_data": email,
                            "reader_email": user_email
                        }).encode()
                    )
                    routing_key=self.queue_name,
                    properties=pika.BasicProperties(
                        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                    ),
                    body=json.dumps({
                        "user_id": user_id,
                        "account_type": "outlook",
                        "user_timezone": str(user_timezone),
                        "email_data": email,
                        "reader_email": user_email
                    })
                )

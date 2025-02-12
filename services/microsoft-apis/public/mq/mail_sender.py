import asyncio, json
import sqlalchemy.exc
from sqlalchemy import select
from zoneinfo import ZoneInfo

import pika, pika.channel, pika.spec
from pika.adapters.asyncio_connection import AsyncioConnection

import sys
sys.path.append('..')
from common import tables

import db
import logging

class MailSenderMQ:
    def __init__(self, host: str, virtual_host: str, username: str, password: str, queue_name: str):
        self._ioloop = asyncio.get_running_loop()
        self.mq_connection = AsyncioConnection(
            parameters=pika.ConnectionParameters(
                host=host, 
                port=5672, 
                virtual_host=virtual_host, 
                credentials=pika.PlainCredentials(username, password)
            ),
            custom_ioloop=self._ioloop,
            on_open_callback=self._conn_open_callback,
            on_open_error_callback=self._conn_failed_callback
        )
        self.queue_name = queue_name
        self.mq_channel = None

        self.__logger = logging.getLogger(__name__)

    def close_conn(self):
        if(self.mq_connection.is_open):
            self.mq_connection.close()    

    def _conn_open_callback(self, conn: AsyncioConnection):
        conn.channel(on_open_callback=self._channel_open_callback)

    def _conn_failed_callback(self, conn: AsyncioConnection, err: BaseException):
        # TODO: error handling
        print("CONN ERROR")

    def _channel_open_callback(self, channel: pika.channel.Channel):
        self.mq_channel = channel

        self.mq_channel.queue_declare(queue=self.queue_name)

    async def send_new_email_to_parse(
        self,
        user_id: str,
        user_email: str,
        user_timezone: ZoneInfo,
        email: dict[str]
    ):
        self.mq_channel.basic_publish(
            exchange="",
            routing_key=self.queue_name,
            body=json.dumps({
                "user_id": user_id,
                "account_type": "outlook",
                "user_timezone": str(user_timezone),
                "email_data": email,
                "reader_email": user_email
            })
        )

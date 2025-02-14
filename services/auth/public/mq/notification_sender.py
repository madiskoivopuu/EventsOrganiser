import asyncio, json

import pika, pika.channel, pika.spec
from pika.adapters.asyncio_connection import AsyncioConnection
from datetime import datetime
from zoneinfo import ZoneInfo
import logging

class NotificationSenderMQ:
    def __init__(self, host: str, virtual_host: str, username: str, password: str):
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

        self.mq_channel.exchange_declare(exchange="notifications", exchange_type="topic")

    async def notify_of_ms_login(self, account_id: str, access_token_expiration: datetime, email: str,
                                 user_timezone: ZoneInfo, access_token: str, refresh_token: str):
        if(self.mq_channel == None):
            raise ConnectionError("MQ Channel has not yet been opened")
        
        self.mq_channel.basic_publish(
            exchange="notifications",
            routing_key="notification.outlook.user_login",
            body=json.dumps({
                "account_id": account_id,
                "email": email,
                "user_timezone": str(user_timezone),
                "access_token": access_token,
                "access_token_expiration": access_token_expiration.isoformat(),
                "refresh_token": refresh_token
            })
        )
        
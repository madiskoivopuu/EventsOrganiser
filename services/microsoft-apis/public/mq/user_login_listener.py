import asyncio, json
import sqlalchemy.exc
from sqlalchemy import select
from zoneinfo import ZoneInfo
from datetime import datetime

import pika, pika.channel, pika.spec
from pika.adapters.asyncio_connection import AsyncioConnection

import sys
sys.path.append('..')
from common import tables

import db
import logging

class LoginListenerMQ:
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
        self.mq_channel.queue_declare(queue="outlook_user_logins")
        self.mq_channel.queue_bind(exchange="notifications", queue="outlook_user_logins", routing_key="notification.outlook.user_login")

        self.mq_channel.basic_consume(queue="outlook_user_logins", on_message_callback=self._on_user_login)

    def _on_user_login(self, channel: pika.channel.Channel, 
                    method: pika.spec.Basic.Deliver, 
                    properties: pika.spec.BasicProperties, 
                    body: bytes):
        self._ioloop.create_task(self.process_login(channel, method, properties, body))

    async def process_login(self, channel: pika.channel.Channel, 
                    method: pika.spec.Basic.Deliver, 
                    properties: pika.spec.BasicProperties, 
                    body: bytes):
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.__logger.error("Unable to decode new user notification due to a programmer JSON formatting error", exc_info=True)
            channel.basic_reject(method.delivery_tag, requeue=False)

        results = await asyncio.gather(
            self.merge_user_info(data),
            self.create_settings(data)
        )
        
        if(all(results) == True):
            channel.basic_ack(method.delivery_tag)
        else:
            channel.basic_reject(method.delivery_tag, requeue=False)

    async def create_settings(self, data: dict) -> bool:
        async with db.async_session() as db_session:
            q = select(tables.SettingsTable) \
                .where(tables.SettingsTable.user_id == data["account_id"])
            user_settings = await db_session.execute(q).scalar_one_or_none()
            if(user_settings != None): # user already has settings...
                return True

            settings_row = tables.SettingsTable()
            settings_row.user_id = data["account_id"]
            settings_row.events_default_timezone = ZoneInfo(data["user_timezone"])

            db_session.add(settings_row)

            try:
                await db_session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                await db_session.rollback()
                if("duplicate" in e._message().lower()):
                    self.__logger.warning(f"Settings for user {data['account_id']} already exist somehow (not overwritten by this notification)")
                else:
                    self.__logger.warning("Unknown IntegrityError when trying to create new settings for user", exc_info=True)
                    return False

        return True

    async def merge_user_info(self, data: dict):
        """
        Creates or updates existing user info
        """

        async with db.async_session() as db_session:
            user_info = tables.UserInfoTable()
            user_info.user_id = data["account_id"]
            user_info.access_token = data["access_token"]
            user_info.access_token_expires = datetime.fromisoformat(data["access_token_expiration"]) 
            user_info.refresh_token = data["refresh_token"]

            db_session.merge(user_info)
            await db_session.commit()

        return True
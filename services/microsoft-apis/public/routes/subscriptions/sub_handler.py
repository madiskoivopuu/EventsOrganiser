import asyncio
import aiohttp

import db
from common import tables
from mq.notifications import NotifiactionMQ
from helpers import query_helpers

class SubscriptionHandler:
    def __init__(self, host: str, virtual_host: str, username: str, password: str):
        self.setting_notifications_mq = NotifiactionMQ(
            host=host,
            virtual_host=virtual_host,
            username=username,
            password=password,
            queue_name="outlook_settings_changes",
            routing_key="notification.outlook.settings_changed",
            notification_callback=self.settings_changed_notification
        )

    async def start(self):
        await self.setting_notifications_mq.open_conn()

    async def stop(self):
        await self.setting_notifications_mq.close_conn()

    async def delete_subscription(self, subscription_id: str) -> bool:
        """
        Deletes a Microsoft Graph email notification subscription

        :param subscription_id: Subscription ID

        :return: True if the deletion was successful, or if there was no subscription to delete.
            Returns False if an error occurred
        """
        async with aiohttp.ClientSession("https://graph.microsoft.com") as session:
            async with session.delete(f"/v1.0/subscriptions/{subscription_id}")
        pass

    async def settings_changed_notification(self, data: dict) -> bool:
        async with db.async_session() as db_session:
            settings_row = tables.SettingsTable(**data)
            user_info = await query_helpers.update_token_db(db_session, settings_row.user_id)
            subscription = await query_helpers.get_email_notification_subscription(db_session, settings_row.user_id)

            if(settings_row.auto_fetch_emails == False):
                if(subscription != None):
                    await self.delete_subscription(subscription.subscription_id)
            else:
                if(subscription == None):
                    pass
    
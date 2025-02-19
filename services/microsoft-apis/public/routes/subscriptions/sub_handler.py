import asyncio
import aiohttp
import base64
from datetime import datetime, timezone, timedelta

import db
from common import tables
from mq.notifications import NotifiactionMQ
from helpers import query_helpers, graph_api

class SubscriptionHandler:
    __SELECTABLE_GRAPH_EMAIL_PROPERTIES = ["id", "subject", "sentDateTime", "receivedDateTime", "body", "conversationId", "conversationIndex", 
                                           "parentFolderId", "importance", "isRead", "isDraft", "hasAttachments", "webLink", "sender", "from", 
                                           "toRecipients", "categories"]

    def __init__(self, host: str, virtual_host: str, username: str, password: str, 
                 domain_url: str, notification_path: str, notification_lifecycle_path: str, secret: str):
        """
        Creates an instance of a subscription handler that partially uses MQ (settings change notifications) to manage subscriptions
        and Microsoft API callbacks

        :param host: IP of the broker
        :param virtual_host: Virtual host name
        :param username: Broker login username
        :param password: Broker login password
        :param domain_url: Scheme and authority of the URL. If no scheme is given, https:// is automatically added
        :param notification_path: Path pointing to where Microsoft APIs should send email notifications
        :param notification_lifecycle_path: Path pointing to where Microsoft APIs should send notification lifecycle updates
        :param secret: Secret string to be used with the subscriptions
        """
        self.setting_notifications_mq = NotifiactionMQ(
            host=host,
            virtual_host=virtual_host,
            username=username,
            password=password,
            queue_name="outlook_settings_changes",
            routing_key="notification.outlook.settings_changed",
            notification_callback=self.settings_changed_notification
        )

        if(not domain_url.startswith("http")):
            domain_url = "https://" + domain_url

        self.domain_url = domain_url.removesuffix("/")
        self.notification_path = notification_path.removeprefix("/")
        self.notification_lifecycle_path = notification_lifecycle_path.removeprefix("/")
        self.secret = secret

    async def start(self):
        await self.setting_notifications_mq.open_conn()

    async def stop(self):
        await self.setting_notifications_mq.close_conn()

    async def settings_changed_notification(self, data: dict) -> bool:
        async with db.async_session() as db_session:
            settings_row = tables.SettingsTable(**data)
            user_info = await query_helpers.update_token_db(db_session, settings_row.user_id)
            subscription = await query_helpers.get_email_notification_subscription(db_session, settings_row.user_id)

            if(settings_row.auto_fetch_emails == False and subscription != None):
                result = await graph_api.delete_subscription(subscription.subscription_id, user_info.access_token)
                if(not result):
                    return False
                
                db_session.delete(settings_row)
                await db_session.commit()

            elif(settings_row.auto_fetch_emails == True and subscription == None):
                subscription_row = tables.EmailSubscriptionsTable()
                subscription_row.user_id = user_info.user_id
                subscription_id, expiration_date = await graph_api.create_subscription(
                    user_info.access_token,
                    f"{self.domain_url}/{self.notification_path}",
                    f"{self.domain_url}/{self.notification_lifecycle_path}",
                    self.secret,
                    "me/messages?$select=id"
                )
                subscription_row.subscription_id = subscription_id
                subscription_row.expires_at = expiration_date

                db_session.merge(subscription_row)
                await db_session.commit()

        return True
import asyncio
import aiohttp
import base64
from datetime import datetime, timezone, timedelta

import db
from common import tables
from mq.notifications import NotifiactionMQ
from helpers import query_helpers, certs

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

    async def delete_subscription(self, subscription_id: str, access_token: str) -> bool:
        """
        Deletes a Microsoft Graph email notification subscription

        :param subscription_id: Subscription ID
        :param access_token: Access token for the user

        :return: True if the deletion was successful, or if there was no subscription to delete.
            Returns False if an error occurred
        """
        async with aiohttp.ClientSession("https://graph.microsoft.com") as session:
            async with session.delete(
                f"/v1.0/subscriptions/{subscription_id}",
                headers={"Authorization": f"Bearer {access_token}"}
            ) as resp:
                if(resp.status == 404 or resp.status == 204):
                    return True
                
        return False
    
    async def create_subscription(self, access_token: str, encryption_cert: bytes, cert_id: int,
                                  expires_in: timedelta = timedelta(minutes=10000)) -> tuple[str, datetime] | None:
        """
        Creates an email listening subscription for a user

        :param access_token: Access token for the user
        :param encryption_cert: X.509 certificate bytes that Microsoft will encrypt rich notification data with
        :param cert_id: Certificate serial number
        :param expires_in: Expiration date for the subscription. Default value is fetched from Microsoft Graph API docs

        :return: Subscription ID and the expiration date if the request was successful, otherwise None
            If a duplicate subscription already exists, then the ID of an already existing subscription is returned
        """

        expiration_date = datetime.now(timezone.utc) + expires_in
        async with aiohttp.ClientSession("https://graph.microsoft.com") as session:
            async with session.post(
                f"/v1.0/subscriptions",
                headers={
                    "Authorization": f"Bearer {access_token}"
                },
                json={
                    "changeType": "created",
                    "notificationUrl": f"{self.domain_url}/{self.notification_path}",
                    "lifecycleNotificationUrl": f"{self.domain_url}/{self.notification_lifecycle_path}",
                    "resource": f"me/messages?$select=id",
                    "includeResourceData": True,
                    "expirationDateTime": expiration_date.isoformat(),
                    "clientState": self.secret
                }
            ) as resp:
                if(resp.status == 201):
                    json_data = resp.json()
                    return (json_data["id"], datetime.fromisoformat(json_data["expirationDateTime"]))
                elif(resp.status == 409): # sub already exists
                    # cant even test it because microsoft docs say one thing (dupe sub not allowed)
                    # but in reality they actually do allow this
                    raise NotImplementedError("This condition was never met during development")
                else:
                    return None

    async def settings_changed_notification(self, data: dict) -> bool:
        async with db.async_session() as db_session:
            settings_row = tables.SettingsTable(**data)
            user_info = await query_helpers.update_token_db(db_session, settings_row.user_id)
            subscription = await query_helpers.get_email_notification_subscription(db_session, settings_row.user_id)

            if(settings_row.auto_fetch_emails == False and subscription != None):
                result = await self.delete_subscription(subscription.subscription_id, user_info.access_token)
                if(not result):
                    return False
                
                db_session.delete(settings_row)
                await db_session.commit()

            elif(settings_row.auto_fetch_emails == True and subscription == None):
                serial_nr, cert, key = certs.generate_selfsigned_cert()

                subscription_row = tables.EmailSubscriptionsTable()
                subscription_row.user_id = user_info.user_id
                subscription_row.encryption_cert_id = serial_nr
                subscription_row.encryption_cert = cert.decode()
                subscription_row.encryption_key = key.decode()

                subscription_id, expiration_date = await self.create_subscription(user_info.access_token, cert, serial_nr)
                subscription_row.subscription_id = subscription_id
                subscription_row.expires_at = expiration_date

                db_session.merge(subscription_row)
                await db_session.commit()

        return True
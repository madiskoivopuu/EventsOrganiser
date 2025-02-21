import asyncio
import aiohttp
import base64
from datetime import datetime, timezone, timedelta
from typing import cast

import db
from common import tables, models
from helpers import query_helpers, graph_api

class SubscriptionHandler:
    def __init__(self, domain_url: str, notification_path: str, notification_lifecycle_path: str, secret: str):
        """
        Creates an instance of a subscription handler that manages Microsoft Graph email subscriptions
        based on events (settings update, lifecycle notifications)

        :param domain_url: Scheme and authority of the URL. If no scheme is given, https:// is automatically added
        :param notification_path: Path pointing to where Microsoft APIs should send email notifications
        :param notification_lifecycle_path: Path pointing to where Microsoft APIs should send notification lifecycle updates
        :param secret: Secret string to be used with the subscriptions
        """

        if(not domain_url.startswith("http")):
            domain_url = "https://" + domain_url

        self.domain_url = domain_url.removesuffix("/")
        self.notification_path = notification_path.removeprefix("/")
        self.notification_lifecycle_path = notification_lifecycle_path.removeprefix("/")
        self.secret = secret

    async def settings_changed_notification(self, settings_row: tables.SettingsTable) -> bool:
        async with db.async_session() as db_session:
            db_session = cast(db.AsyncSession, db_session) # IDE thing
            user_info = await query_helpers.update_token_db(db_session, settings_row.user_id)
            subscription_row = await query_helpers.get_email_notification_subscription(db_session, user_id=settings_row.user_id)

            if(settings_row.auto_fetch_emails == False and subscription_row != None):
                result = await graph_api.delete_subscription(subscription_row.subscription_id, user_info.access_token)
                if(not result):
                    return False
                
                await db_session.delete(subscription_row)
                await db_session.commit()

            elif(settings_row.auto_fetch_emails == True and subscription_row == None):
                subscription_row = tables.EmailSubscriptionsTable()
                subscription_row.user_id = user_info.user_id
                subscription_result = await graph_api.create_subscription(
                    user_info.access_token,
                    f"{self.domain_url}/{self.notification_path}",
                    f"{self.domain_url}/{self.notification_lifecycle_path}",
                    self.secret,
                    "me/messages"
                )
                if(subscription_result == None):
                    return False

                subscription_id, expiration_date = subscription_result
                subscription_row.subscription_id = subscription_id
                subscription_row.expires_at = expiration_date

                try:
                    await db_session.merge(subscription_row)
                    await db_session.commit()
                except:
                    # try to clean up the subscription somehow
                    await graph_api.delete_subscription(subscription_id, user_info.access_token)
                    return False

        return True
    
    async def _subscription_deleted_notification(self, subscription_data: models._NotificationData) -> bool:
        async with db.async_session() as db_session:
            db_session = cast(db.AsyncSession, db_session) # IDE thing
            subscription_row = await query_helpers.get_email_notification_subscription(db_session, sub_id=subscription_data.subscription_id)
            if(subscription_row == None): # subscription most likely deleted by user
                return True
            
            user_settings = await query_helpers.get_settings(db_session, subscription_row.user_id)
            if(user_settings.auto_fetch_emails == False):
                return True
            
            user_info = await query_helpers.update_token_db(db_session, subscription_row.user_id)
            if(user_info.access_token == None): # login expired
                return True
            
            subscription_result = await graph_api.create_subscription(
                user_info.access_token,
                f"{self.domain_url}/{self.notification_path}",
                f"{self.domain_url}/{self.notification_lifecycle_path}",
                self.secret,
                "me/messages"
            )
            if(subscription_result == None):
                return False
            
            subscription_id, expiration_date = subscription_result
            subscription_row.subscription_id = subscription_id
            subscription_row.expires_at = expiration_date

            try:
                await db_session.merge()
                await db_session.commit()
            except:
                # try to clean up the subscription hopefully...
                await graph_api.delete_subscription(subscription_id, user_info.access_token)
                return False

        return True

    async def _subscription_reauthorize_notification(self, subscription_data: models._NotificationData) -> bool:
        async with db.async_session() as db_session:
            db_session = cast(db.AsyncSession, db_session) # IDE thing
            subscription_row = await query_helpers.get_email_notification_subscription(db_session, sub_id=subscription_data.subscription_id)
            if(subscription_row == None): # subscription most likely deleted by user
                return True
            
            user_settings = await query_helpers.get_settings(db_session, subscription_row.user_id)
            if(user_settings.auto_fetch_emails == False):
                return True
            
            user_info = await query_helpers.update_token_db(db_session, subscription_row.user_id)
            if(user_info.access_token == None): # login expired
                return True
            
            result = await graph_api.extend_subscription(subscription_data.subscription_id, user_info.access_token)
            if(result == None):
                return False
            
            sub_exists, new_exp = result
            if(not sub_exists):
                return True
            
            subscription_row.expires_at = new_exp
            await db_session.merge(subscription_row)
            await db_session.commit()
            
        return True
    
    async def subscription_missed_data_notification(self, subscription_data: models._NotificationData) -> bool:
        raise NotImplementedError("todo")
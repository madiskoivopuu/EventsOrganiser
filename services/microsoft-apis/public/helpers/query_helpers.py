import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from zoneinfo import ZoneInfo

from common import tables
import server_config
from helpers import auth, graph_api

async def get_or_create_timezone(db_session: AsyncSession, tz: ZoneInfo) -> tables.TimezoneTable:
    q = select(tables.TimezoneTable) \
        .where(
            tables.TimezoneTable.timezone == tz
        )
    found_timezone = (await db_session.execute(q)).unique().scalar_one_or_none()
    if(found_timezone != None):
        return found_timezone
    else:
        timezone = tables.TimezoneTable()
        timezone.timezone = tz
        return timezone
    
async def get_settings(db_session: AsyncSession, user_id: str) -> tables.SettingsTable:
    """
    Fetches settings for a user

    :param db_session: An existing database session
    :param user_id: User id (oid) of the account

    :raises: An exception if the row does not exist

    :return: Table row with user settings
    """

    q = select(tables.SettingsTable) \
        .where(
            tables.SettingsTable.user_id == user_id
        )

    return (await db_session.execute(q)).unique().scalar_one()

async def get_email_notification_subscription(db_session: AsyncSession, user_id: str) -> tables.EmailSubscriptionsTable | None:
    """
    Fetches the email subscription row for a user

    :param db_session: An existing database session
    :param user_id: User id (oid) of the account

    :return: The email subscription row if it exists, otherwise None
    """

    q = select(tables.EmailSubscriptionsTable) \
        .where(
            tables.EmailSubscriptionsTable.user_id == user_id
        )
    
    return (await db_session.execute(q)).scalar_one_or_none()

async def update_token_db(db_session: AsyncSession, user_id: str) -> tables.UserInfoTable:
    """
    Updates user data row in MySQL with a new access token, if needed. 
    Stores the new access token in DB, or if refresh token has expired, clears refresh token & access token from db.

    :param db_session: An existing database session
    :param user_id: User id (oid) of the account

    :return: Updated user info row
    """

    q = select(tables.UserInfoTable) \
        .where(tables.UserInfoTable.user_id == user_id) \
        .with_for_update()
    
    user_info = (await db_session.execute(q)).scalar_one()

    new_token, new_exp, new_refresh_token = await graph_api.update_token_if_needed(
        access_token=user_info.access_token,
        expires_at=user_info.access_token_expires.replace(tzinfo=ZoneInfo("UTC")),
        refresh_token=user_info.refresh_token,
        client_id=server_config.MICROSOFT_APP_CLIENT_ID,
        client_secret=server_config.MICROSOFT_APP_SECRET,
        scopes=server_config.MICROSOFT_SCOPES + ["openid", "profile", "offline_access"]
    )
    if(new_token == None):
        user_info.access_token = None
        user_info.access_token_expires = None
        user_info.refresh_token = None
    elif(new_token != user_info.access_token):
        user_info.access_token = new_token
        user_info.access_token_expires = new_exp
        user_info.refresh_token = new_refresh_token

    await db_session.commit()

    return user_info
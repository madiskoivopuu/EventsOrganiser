import asyncio

from fastapi import FastAPI, APIRouter, Request, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from datetime import timedelta
import itertools

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from contextlib import asynccontextmanager

import logging
logging.basicConfig(level=logging.INFO)

from typing import cast

from common import models, tables
import os, db
import server_config
from helpers import query_helpers, graph_api
from .sub_handler import SubscriptionHandler
from mq.mail_sender import MailSenderMQ, ParseMailsRequest

__logger = logging.getLogger(__name__)

@asynccontextmanager
async def app_lifecycle(api: FastAPI):
    subscription_handler = SubscriptionHandler(
        host=server_config.RABBITMQ_HOST,
        virtual_host=server_config.RABBITMQ_VIRTUALHOST,
        username=server_config.RABBITMQ_USERNAME,
        password=server_config.RABBITMQ_PASSWORD,
        domain_url=server_config.DOMAIN_URL,
        notification_path="/subscriptions/new_email",
        notification_lifecycle_path="/subscriptions/email_sub_lifecycle",
        secret=server_config.MICROSOFT_CALLBACK_SECRET
    )
    mail_sender_mq = MailSenderMQ(
        host=server_config.RABBITMQ_HOST,
        virtual_host=server_config.RABBITMQ_VIRTUALHOST,
        username=server_config.RABBITMQ_USERNAME,
        password=server_config.RABBITMQ_PASSWORD,
        queue_name=server_config.RABBITMQ_EMAILS_QUEUE
    )

    await subscription_handler.start()
    await mail_sender_mq.open_conn()

    yield {
        "subscription_handler": subscription_handler,
        "mail_sender_mq": mail_sender_mq
    }

    await subscription_handler.stop()
    await mail_sender_mq.close_conn()

subscriptions_router = APIRouter(
    prefix="/api/microsoft",
    lifespan=app_lifecycle
)


async def fetch_emails_batched(
        fetch_data: list[tuple[str, tables.UserInfoTable, tables.SettingsTable]], 
        batch_size: int = 10) -> list[ParseMailsRequest]:
    """
    Sends batched requests to Microsoft Graph API /me/messages endpoint to fetch emails.

    :param ids_and_tokens: List of tuples consisting of email ID and access token

    :raises HTTPException: if any request in the batch fails

    :return: A list of parse request objects
    """
    results = []
    for batch in itertools.batched(fetch_data, batch_size):
        tasks: list[asyncio.Task] = []
        for item in batch:
            async with asyncio.TaskGroup() as tg:
                tasks.append(tg.create_task(graph_api.get_message(item[0], item[1].access_token)))

        for item, task in zip(batch, tasks):
            user_info = item[1]
            user_settings = item[2]
            data = task.result()
            if(data["resp"].status != 200):
                raise HTTPException(status_code=500, detail="Failed to fetch one email")

            results.append(
                ParseMailsRequest(
                    user_id=user_info.user_id,
                    user_email=user_info.user_email,
                    user_timezone=user_settings.timezone.timezone,
                    email=data["json_data"]
                )
            )

    return results

@subscriptions_router.post("/subscriptions/new_email", status_code=200)
async def new_email(
    new_emails: models.NewEmailPostRequest | None,
    request: Request,
    db_session: AsyncSession = Depends(db.start_session)
) -> models.SettingsGetResponse:
    # new subscription validation
    if("validationToken" in request.query_params):
        return PlainTextResponse(
            content=request.query_params.get("validationToken")
        )

    if(new_emails == None):
        raise HTTPException(status_code=400)

    ids_and_users: list[tuple[str, str]] = []
    for data in new_emails.value:
        if(data.client_state != server_config.MICROSOFT_CALLBACK_SECRET):
            __logger.warning("Client state given by notification does not match the server's callback secret")
            continue

        q = select(tables.EmailSubscriptionsTable) \
        .where(
            tables.EmailSubscriptionsTable.subscription_id == data.subscription_id
        )
        subscription_row = (await db_session.execute(q)).scalar_one_or_none()
        if(subscription_row == None):
            continue

        user_settings = await query_helpers.get_settings(db_session, subscription_row.user_id)
        user_info = await query_helpers.update_token_db(db_session, subscription_row.user_id)
        if(user_info.access_token == None):
            continue
        if(user_settings.auto_fetch_emails == False):
            continue

        ids_and_users.append((data.resource_data.id, user_info, user_settings))

    email_parse_requests = await fetch_emails_batched(ids_and_users)

    await cast(MailSenderMQ, request.state.mail_sender_mq).send_new_emails_to_parse(
        email_parse_requests
    )

    return

@subscriptions_router.post("/subscriptions/email_sub_lifecycle")
async def subscription_lifecycle():
    pass
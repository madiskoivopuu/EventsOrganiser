import aiohttp
import security

from fastapi import FastAPI, APIRouter, Request, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from contextlib import asynccontextmanager

import logging
logging.basicConfig(level=logging.INFO)

from common import models, tables

import server_config
import os, db

import server_config
from sub_handler import SubscriptionHandler

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

    await subscription_handler.start()

    yield {"subscription_handler": subscription_handler}

    await subscription_handler.stop()

subscriptions_router = APIRouter(
    prefix="/api/microsoft",
    lifespan=app_lifecycle
)

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

    full_emails = []
    for data in new_emails.value:
        if(data.client_state != server_config.MICROSOFT_CALLBACK_SECRET):
            __logger.warning("Client state given by notification does not match the server's callback secret")
            continue

        q = select(tables.EmailSubscriptionsTable) \
        .where(
            tables.EmailSubscriptionsTable.subscription_id == data.subscriptionId
        )
        subscription_row = (await db_session.execute(q)).scalar_one_or_none()
        if(subscription_row == None):
            continue

        
    
    return (await db_session.execute(q)).scalar_one_or_none()

@subscriptions_router.post("/subscriptions/email_sub_lifecycle")
async def subscription_lifecycle():
    pass
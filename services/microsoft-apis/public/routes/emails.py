from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi_server_session import Session, SessionManager, AsyncRedisSessionInterface
from redis import asyncio as aioredis
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload

import asyncio
import logging
logging.basicConfig(level=logging.INFO)

import sys
sys.path.append('..')
from common import models, tables

import server_config, db
from helpers import auth
from helpers.auth import UserData
from mq.mail_sender import MailSenderMQ
from helpers import query_helpers, graph_api

__logger = logging.getLogger(__name__)
emails_router = APIRouter(
    prefix="/api/microsoft"
)

mail_sender_mq = MailSenderMQ(
    host=server_config.RABBITMQ_HOST,
    virtual_host=server_config.RABBITMQ_VIRTUALHOST,
    username=server_config.RABBITMQ_USERNAME,
    password=server_config.RABBITMQ_PASSWORD
)

@emails_router.post("/emails/fetch_new", status_code=200)
async def new_email(
    user: UserData = Depends(auth.authenticate_user),
    db_session: AsyncSession = Depends(db.start_session)
) -> models.FetchNewEmailsGetResponse:
    user_data = await query_helpers.update_token_db(user, db_session)
    user_settings = await query_helpers.get_settings(db_session, user.account_id)

    emails = graph_api.read_emails_after_date(
        user_data.access_token,
        after_date=user_data.most_recent_fetched_email,
        select=["id"]
    )

    if(len(emails) != 0):
        most_recent = None
        for email in emails:
            sent_date = datetime.fromisoformat(email)
            if(most_recent == None or sent_date > most_recent):
                most_recent = sent_date

        user_data.most_recent_fetched_email = most_recent

    for email in emails:
        response = await graph_api.get_message(
            email["id"],
            user_data.access_token
        )
        if(response["resp"].status != 200):
            raise HTTPException(status_code=500, detail=f"Failed to fetch an email with ID {email['id']}")

        await mail_sender_mq.send_new_email_to_parse(
            user_data.user_id,
            user_data.user_email,
            user_settings.events_default_timezone.timezone,
            response["resp_json"]
        )

    await db_session.commit() # TODO: check if this can still update after the first commit in update_token_db

    resp = models.FetchNewEmailsGetResponse()
    resp.count = len(emails)
    return resp

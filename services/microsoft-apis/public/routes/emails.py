from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi_server_session import Session, SessionManager, AsyncRedisSessionInterface
from redis import asyncio as aioredis
from datetime import timezone

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

__emails_queue = asyncio.Queue()

@emails_router.post("/emails/fetch_new", status_code=200)
async def new_email(
    user: UserData = Depends(auth.authenticate_user),
    db_session: AsyncSession = Depends(db.start_session)
) -> models.FetchNewEmailsGetResponse:
    user_data = await query_helpers.update_token_db(user, db_session)

    emails = graph_api.read_emails_after_date(
        user_data.access_token,
        after_date=user_data.most_recent_fetched_email,
        select=["id"]
    )
    if(len(emails) != 0):
        data = {
            "account_id": user_data.user_id,
            "email_ids": emails
        }
        await __emails_queue.put(data)

    resp = models.FetchNewEmailsGetResponse()
    resp.count = len(emails)
    return resp


async def loop_send_new_emails_to_parser():
    global __emails_queue

    mail_sender_mq = MailSenderMQ(
        host=server_config.RABBITMQ_HOST,
        virtual_host=server_config.RABBITMQ_VIRTUALHOST,
        username=server_config.RABBITMQ_USERNAME,
        password=server_config.RABBITMQ_PASSWORD
    )

    while True:
        item = await __emails_queue.get()

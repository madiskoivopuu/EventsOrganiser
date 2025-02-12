from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi_server_session import Session, SessionManager, AsyncRedisSessionInterface
from redis import asyncio as aioredis
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload

import logging
logging.basicConfig(level=logging.INFO)

import sys
sys.path.append('..')
from common import models, tables

import server_config
import os, db

import server_config
from helpers import auth
from helpers import db_helpers
from helpers.auth import UserData

__logger = logging.getLogger(__name__)
settings_router = APIRouter(
    prefix="/api/microsoft"
)

@settings_router.get("/settings")
async def get_settings(
    user: UserData = Depends(auth.authenticate_user),
    db_session: AsyncSession = Depends(db.start_session)
) -> models.SettingsGetResponse:
    query = select(tables.SettingsTable) \
            .where(
                tables.SettingsTable.user_id == user.account_id,
                tables.SettingsTable.user_acc_type == user.account_type
            )
    
    query_result = await db_session.execute(query)

    return models.SettingsGetResponse.model_validate(query_result.scalar_one())

@settings_router.patch("/settings", status_code=204)
async def update_settings(
    new_settings: models.SettingsPostRequest,
    user: UserData = Depends(auth.authenticate_user),
    db_session: AsyncSession = Depends(db.start_session)
):
    settings_row = tables.SettingsTable()
    settings_row.user_id = user.account_id
    settings_row.user_acc_type = user.account_type

    settings_row.auto_fetch_emails = new_settings.auto_fetch_emails
    settings_row.events_default_timezone = db_helpers.get_or_create_timezone(db_session, new_settings.events_default_timezone)

    await db_session.merge(settings_row)
    await db_session.commit()

    return
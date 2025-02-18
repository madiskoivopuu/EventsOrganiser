from fastapi import APIRouter, Request, Response, HTTPException, Depends
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload

import logging
logging.basicConfig(level=logging.INFO)

from common import models, tables

import server_config
import os, db

import server_config
from helpers import auth
from helpers import query_helpers
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
    settings_row = await query_helpers.get_settings(db_session, user.account_id)

    return models.SettingsGetResponse(
        auto_fetch_emails=settings_row.auto_fetch_emails,
        timezone=settings_row.timezone.timezone
    )

@settings_router.patch("/settings", status_code=204)
async def update_settings(
    new_settings: models.SettingsPostRequest,
    user: UserData = Depends(auth.authenticate_user),
    db_session: AsyncSession = Depends(db.start_session)
):
    prev_settings = await query_helpers.get_settings(db_session, user.account_id)

    prev_settings.auto_fetch_emails = new_settings.auto_fetch_emails
    prev_settings.timezone = await query_helpers.get_or_create_timezone(db_session, new_settings.timezone)

    await db_session.merge(prev_settings)
    await db_session.commit()

    return
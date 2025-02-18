from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import PlainTextResponse
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
from helpers.auth import UserData

__logger = logging.getLogger(__name__)
subscriptions_router = APIRouter(
    prefix="/api/microsoft"
)

@subscriptions_router.post("/subscriptions/new_email", status_code=200)
async def new_email(
    request: Request,
    user: UserData = Depends(auth.authenticate_user),
    db_session: AsyncSession = Depends(db.start_session)
) -> models.SettingsGetResponse:
    # new subscription validation
    if("validationToken" in request.path_params):
        return PlainTextResponse(
            content=request.path_params.get("validationToken")
        )
    pass

@subscriptions_router.post("/subscriptions/email_sub_lifecycle")
async def subscription_lifecycle():
    pass
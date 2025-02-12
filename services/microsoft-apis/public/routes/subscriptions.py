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
from helpers.auth import UserData

__logger = logging.getLogger(__name__)
subscriptions_router = APIRouter(
    prefix="/api/microsoft"
)

@subscriptions_router.post("/subscriptions/new_email")
async def new_email(
    user: UserData = Depends(auth.authenticate_user),
    db_session: AsyncSession = Depends(db.start_session)
) -> models.SettingsGetResponse:
    pass
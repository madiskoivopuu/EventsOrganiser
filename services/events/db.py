import asyncio

from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from asyncio import current_task

import server_config

url = URL.create(
    drivername="mysql+asyncmy",
    username=server_config.MYSQL_EVENTS_USER,
    password=server_config.MYSQL_EVENTS_PASSWORD,
    host=server_config.MYSQL_HOST,
    database="events",
    port=3306
)
engine = create_async_engine(url)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def start_session() -> AsyncSession:
    async with async_session() as session:
        yield session
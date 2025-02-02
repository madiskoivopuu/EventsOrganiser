import asyncio, db, os, uuid
from datetime import datetime

from sqlalchemy import Column, Table, ForeignKey, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.types import Uuid

from typing import Optional

import models

class Base(DeclarativeBase):
    pass

tags_to_events = Table(
    "tags_to_events",
    Base.metadata,
    Column("event_id", ForeignKey("events.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

class TagsTable(Base):
    __tablename__ = "tags"

    id: Mapped[int]  = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)

class EventsTable(Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint("end_date_utc IS NOT NULL", name="date_check"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_acc_type: Mapped[models.AccountType] = mapped_column(nullable=False, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(256))
    
    event_name: Mapped[str] = mapped_column(String(128))
    start_date_utc: Mapped[Optional[datetime]] # Always stores UTC ISO-8601 datetime
    end_date_utc: Mapped[datetime] # Always stores UTC ISO-8601 datetime
    address: Mapped[str] = mapped_column(String(256))

    tags: Mapped[list[TagsTable]] = relationship(secondary=tags_to_events, lazy="joined")

class CalendarLinksTable(Base):
    __tablename__ = "calendar_links"
    user_id: Mapped[str] = mapped_column(String(256), primary_key=True)
    user_acc_type: Mapped[models.AccountType] = mapped_column(nullable=False, primary_key=True)
    calendar_identifier: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4)

async def create_tables() -> None:
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# sometimes there is an event loop running, other times there isn't; looks like this has something to do with the hot reloader?
if(os.getenv("DEV_MODE") == "1"):
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(create_tables())
    except RuntimeError:
        asyncio.run(create_tables())
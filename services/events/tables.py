import asyncio
import db
from datetime import datetime
import os

from sqlalchemy import Column, Table, ForeignKey, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase, relationship

from typing import Optional

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
        CheckConstraint("start_date IS NOT NULL OR end_date IS NOT NULL", name="date_check"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    mail_acc_type: Mapped[int]
    mail_acc_id: Mapped[str] = mapped_column(String(256))
    
    event_name: Mapped[str] = mapped_column(String(128))
    start_date: Mapped[Optional[datetime]] # Always stores UTC ISO-8601 datetime
    end_date: Mapped[Optional[datetime]] # Always stores UTC ISO-8601 datetime
    country: Mapped[str] = mapped_column(String(64))
    city: Mapped[str] = mapped_column(String(64))
    address: Mapped[str] = mapped_column(String(64))
    room: Mapped[str] = mapped_column(String(64))

    tags: Mapped[list[TagsTable]] = relationship(secondary=tags_to_events, lazy="joined")

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
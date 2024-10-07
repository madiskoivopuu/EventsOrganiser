import db
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Table, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase, relationship

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
    name: Mapped[str] = mapped_column(String(64))

class EventsTable(Base):
    __tablename__ = "events"

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
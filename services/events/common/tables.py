import uuid
from zoneinfo import ZoneInfo
from datetime import datetime

from sqlalchemy import Column, Table, ForeignKey, String, CheckConstraint
import sqlalchemy.types as types
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase, relationship

from typing import Optional

from . import models


class TimezoneSQLType(types.TypeDecorator):
    impl = types.VARCHAR

    def process_bind_param(self, value: ZoneInfo, dialect) -> str:
        return value.key
    
    def process_result_value(self, value: str, dialect) -> ZoneInfo:
        return ZoneInfo(value)


class Base(DeclarativeBase):
    type_annotation_map = {
        ZoneInfo: TimezoneSQLType
    }

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
    user_acc_type: Mapped[str] = mapped_column(String(64), nullable=False, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(256))
    
    event_name: Mapped[str] = mapped_column(String(128))
    start_date_utc: Mapped[Optional[datetime]] # Always stores UTC ISO-8601 datetime
    end_date_utc: Mapped[datetime] # Always stores UTC ISO-8601 datetime
    address: Mapped[str] = mapped_column(String(256))
    email_link: Mapped[str] = mapped_column(String(256))

    tags: Mapped[list[TagsTable]] = relationship(secondary=tags_to_events, lazy="joined")

class CalendarLinksTable(Base):
    __tablename__ = "calendar_links"

    user_id: Mapped[str] = mapped_column(String(256), primary_key=True)
    user_acc_type: Mapped[str] = mapped_column(String(64), nullable=False, primary_key=True)
    calendar_identifier: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4)

class TimezoneTable(Base):
    __tablename__ = "timezones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timezone: Mapped[ZoneInfo] = mapped_column(TimezoneSQLType(64), nullable=False)

    _related_settings: Mapped["EventSettingsTable"] = relationship(back_populates="timezone")

class EventSettingsTable(Base):
    __tablename__ = "event_settings"

    user_id: Mapped[str] = mapped_column(String(256), primary_key=True)
    user_acc_type: Mapped[str] = mapped_column(String(64), nullable=False, primary_key=True)
    
    timezone_id: Mapped[int] = mapped_column(ForeignKey("timezones.id"))
    timezone: Mapped[TimezoneTable] = relationship(back_populates="_related_settings")
import uuid
from zoneinfo import ZoneInfo
from datetime import datetime, tzinfo

from sqlalchemy import DateTime, ForeignKey, String
import sqlalchemy.types as types
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase, relationship, MappedAsDataclass

from typing import Optional

class Base(DeclarativeBase):
    pass

def tz_aware(dt: datetime) -> tzinfo | None:
    if(dt is not None and 
       dt.tzinfo is not None and 
       dt.tzinfo.utcoffset(dt) is not None):
        return dt.tzinfo
    else:
        return None

class _TimezoneSQLType(types.TypeDecorator):
    impl = types.VARCHAR
    cache_ok = True

    def process_bind_param(self, value: ZoneInfo, dialect) -> str:
        return value.key
    
    def process_result_value(self, value: str, dialect) -> ZoneInfo:
        return ZoneInfo(value)

class _UTCDateTimeSQLType(types.TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime, dialect) -> datetime:
        if(value is not None):
            value = value.astimezone(ZoneInfo("UTC"))
        return value
    
    def process_result_value(self, value: datetime, dialect) -> datetime:
        if(value is not None):
            value = value.replace(tzinfo=ZoneInfo("UTC"))
        return value
    
class UserInfoTable(Base):
    __tablename__ = "user_info"

    user_id: Mapped[str] = mapped_column(String(256), primary_key=True, unique=True)
    
    user_email: Mapped[str] = mapped_column(String(256))
    access_token: Mapped[str] = mapped_column(String(4096), nullable=True)
    access_token_expires: Mapped[datetime] = mapped_column(_UTCDateTimeSQLType(), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(2048), nullable=True)
    most_recent_fetched_email_utc: Mapped[datetime] = mapped_column(_UTCDateTimeSQLType(), nullable=True)

class TimezoneTable(Base):
    __tablename__ = "timezones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timezone: Mapped[ZoneInfo] = mapped_column(_TimezoneSQLType(64), nullable=False, unique=True)

    _related_settings: Mapped[list["SettingsTable"]] = relationship(back_populates="timezone", lazy="joined")

class EmailSubscriptionsTable(Base):
    __tablename__ = "email_subscriptions"

    user_id: Mapped[str] = mapped_column(String(256), primary_key=True, unique=True)
    subscription_id: Mapped[str] = mapped_column(String(256))
    expires_at: Mapped[datetime] = mapped_column(_UTCDateTimeSQLType())

class SettingsTable(MappedAsDataclass, Base):
    __tablename__ = "settings"

    user_id: Mapped[str] = mapped_column(String(256), primary_key=True, unique=True)

    timezone_id: Mapped[int] = mapped_column(ForeignKey("timezones.id"))
    timezone: Mapped[TimezoneTable] = relationship(back_populates="_related_settings", lazy="joined")
    auto_fetch_emails: Mapped[bool] = mapped_column(default=False)
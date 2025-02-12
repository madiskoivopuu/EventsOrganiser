import uuid
from zoneinfo import ZoneInfo
from datetime import datetime

from sqlalchemy import Column, Table, ForeignKey, String, CheckConstraint
import sqlalchemy.types as types
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase, relationship

from typing import Optional

class Base(DeclarativeBase):
    pass

class _TimezoneSQLType(types.TypeDecorator):
    impl = types.VARCHAR

    def process_bind_param(self, value: ZoneInfo, dialect) -> str:
        return value.key
    
    def process_result_value(self, value: str, dialect) -> ZoneInfo:
        return ZoneInfo(value)

class UserInfoTable(Base):
    __tablename__ = "user_info"

    user_id: Mapped[str] = mapped_column(String(256), primary_key=True, unique=True)
    
    most_recent_fetched_email: Mapped[datetime] = mapped_column(nullable=True)
    access_token: Mapped[str] = mapped_column(String(4096), nullable=True)
    access_token_expires: Mapped[datetime] = mapped_column(nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(2048), nullable=True)

class TimezoneTable(Base):
    __tablename__ = "timezones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timezone: Mapped[ZoneInfo] = mapped_column(_TimezoneSQLType(64), nullable=False, unique=True)

    _related_settings: Mapped["SettingsTable"] = relationship(back_populates="timezone")

class UserEmailSubscriptionTable(Base):
    __tablename__ = "email_subscriptions"

    user_id: Mapped[str] = mapped_column(String(256), primary_key=True, unique=True)
    subscription_id: Mapped[str] = mapped_column(String(256))

class SettingsTable(Base):
    __tablename__ = "settings"

    user_id: Mapped[str] = mapped_column(String(256), primary_key=True, unique=True)

    auto_fetch_emails: Mapped[bool] = mapped_column(default=False)
    events_default_timezone_id: Mapped[int] = mapped_column(ForeignKey("timezones.id"))
    events_default_timezone: Mapped[TimezoneTable] = relationship(back_populates="_related_settings")
import pydantic
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

from typing import Literal, Optional
from typing_extensions import Self
from fastapi import Query, Body

from zoneinfo import ZoneInfo

class SettingsPostRequest(BaseModel):
    auto_fetch_emails: bool = Field(description="Enable server to get automatic notifications of new emails for a user")
    timezone: ZoneInfo = Field(description="IANA timezone identifier")

class SettingsGetResponse(SettingsPostRequest):
    model_config = ConfigDict(from_attributes=True)

    pass

class _ResourceData(BaseModel):
    id: str

class _NotificationData(BaseModel):
    change_type: str = Field(alias="changeType")
    client_state: str = Field(alias="clientState")
    subscription_id: str = Field(alias="subscriptionId")
    resource_data: _ResourceData = Field(alias="resourceData")

class NewEmailPostRequest(BaseModel):
    value: list[_NotificationData]

class FetchNewEmailsGetResponse(BaseModel):
    count: int
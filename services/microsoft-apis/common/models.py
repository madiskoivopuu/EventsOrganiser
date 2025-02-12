import pydantic
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

from typing import Literal, Optional
from typing_extensions import Self
from fastapi import Query, Body

from zoneinfo import ZoneInfo

class SettingsPostRequest(BaseModel):
    auto_fetch_emails: bool
    events_default_timezone: ZoneInfo

class SettingsGetResponse(SettingsPostRequest):
    pass

class FetchNewEmailsGetResponse(BaseModel):
    count: int
import pydantic
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

from typing import Literal, Optional
from typing_extensions import Self
from fastapi import Query, Body

from datetime import datetime
import pytz

# Based on https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive , checks if datetime object knows what timezone it is in
def tz_aware(dt):
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None

class AccountType(Enum):
    OUTLOOK = "outlook"
    #GMAIL = "gmail"

class EventsGetRequest(BaseModel):
    direction: Literal["forward", "backward"] = Field(Query(description="Tells the API endpoint whether to fetch events before or after a given date"))
    from_time: datetime = Field(Query(description="An ISO-8601 date string specifying the date to fetch events from (or up to). If no timezone is provided, then the time will be treated as an UTC timestamp."))

class Tag(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

class EventBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_name: str = Field(Body(description="Title given by the LLM for the event"))
    start_date: Optional[datetime] = Field(Body(description="UTC timestamp for event start date"))
    end_date: Optional[datetime] = Field(Body(description="UTC timestamp for event end date"))
    country: str = Field(Body())
    city: str = Field(Body())
    address: str = Field(Body())
    room: str = Field(Body())

    @pydantic.model_validator(mode="after")
    def validate_multiple_fields(self) -> Self:
        if(self.start_date == None and self.end_date == None):
            raise ValueError("'start_date' and 'end_date' cannot be none at the same time")
        
        if(self.start_date != None and not tz_aware(self.start_date)):
            self.start_date = self.start_date.replace(tzinfo=pytz.UTC)

        if(self.end_date != None and not tz_aware(self.end_date)):
            self.end_date = self.end_date.replace(tzinfo=pytz.UTC)

        return self

class EventsGetResponse(EventBase):
    id: int = Field(Body(description="Event identifier in database"))
    tags: list[Tag] = Field(Body())

"""class EventPostRequest(EventBase):
    mail_acc_type: int = Field(Body())
    mail_acc_id: str = Field(Body())
    tags: list[str] = Field(Body())"""

class GenerateCalendarLinkResponse(BaseModel):
    link: str = Field(Body(description="Calendar link's full URL"))
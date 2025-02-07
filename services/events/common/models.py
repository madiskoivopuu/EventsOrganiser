import pydantic
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

from typing import Literal, Optional
from typing_extensions import Self
from fastapi import Query, Body

from datetime import datetime, tzinfo
import pytz

# Based on https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive , checks if datetime object knows what timezone it is in
def tz_aware(dt) -> tzinfo | None:
    if(dt is not None and 
       dt.tzinfo is not None and 
       dt.tzinfo.utcoffset(dt) is not None):
        return dt.tzinfo
    else:
        return None

class Tag(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

class EventBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_name: str = Field(description="Title given by the LLM for the event")
    start_date_utc: Optional[datetime] = Field(None, description="Timestamp for event start date. If no timezone is specified, the timestamp will be treated as UTC.")
    end_date_utc: datetime = Field(description="Timestamp for event end date. If no timezone is specified, the timestamp will be treated as UTC.")
    address: str

    @pydantic.model_validator(mode="after")
    def validate_multiple_fields(self) -> Self:
        if(self.end_date_utc == None):
            raise ValueError("'end_date' cannot be none")
        
        if(self.start_date_utc != None and not tz_aware(self.start_date_utc)):
            self.start_date_utc = self.start_date_utc.replace(tzinfo=pytz.UTC)

        if(self.end_date_utc != None and not tz_aware(self.end_date_utc)):
            self.end_date_utc = self.end_date_utc.replace(tzinfo=pytz.UTC)

        return self

class EventsGetRequest(BaseModel):
    direction: Literal["forward", "backward"] = Field(Query(description="Tells the API endpoint whether to fetch events before or after a given date"))
    from_time: datetime = Field(Query(description="An ISO-8601 date-time string specifying the date to fetch events from (or up to). If no timezone is provided, then the time will be treated as an UTC timestamp."))

class EventsGetResponse(EventBase):
    id: int = Field(description="Event identifier in database")
    tags: list[Tag] = Field(description="Category tags for the event. Only tags from the /events/tags endpoint are allowed. Only tags from the /events/tags endpoint are going to be included. Tags that aren't defined there will be ignored.")


class EventsUpdateRequest(EventBase):
    tags: list[str] = Field(description="Category tags for the event. Only tags from the /events/tags endpoint are going to be included. Tags that aren't defined there will be ignored.")


class CalendarLinkResponse(BaseModel):
    link: str = Field(description="Calendar link's full URL")
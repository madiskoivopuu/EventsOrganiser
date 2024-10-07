from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, List, Optional
from fastapi import Query, Body

from datetime import datetime

class EventsRequest(BaseModel):
    direction: Literal["forward", "backward"] = Field(description="Tells the API endpoint whether to fetch events before or after a given date")
    from_time: datetime = Field(description="An ISO-8601 date string specifying the date to fetch events from (or up to). If no timezone is provided, then the time will be treated as an UTC timestamp.")

class Tag(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

class Event(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(title="Event identifier in database")
    event_name: str = Field(title="Title given by the LLM for the event")
    start_date: Optional[datetime] = Field(title="UTC timestamp for event start date")
    end_date: Optional[datetime] = Field(title="UTC timestamp for event end date")
    country: str
    city: str
    address: str
    room: str
    tags: List[Tag]

class NewParsedEvent(Event):
    mail_acc_type: int
    mail_acc_id: str
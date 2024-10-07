from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from fastapi import Query

from datetime import datetime

class EventsRequest(BaseModel):
    direction: Literal["forward", "backward"] = Field(Query(description="Tells the API endpoint whether to fetch events before or after a given date"))
    from_time: datetime = Field(Query(description="An ISO-8601 date string specifying the date to fetch events from (or up to). If no timezone is provided, then the time will be treated as an UTC timestamp."))

class Tag(BaseModel):
    id: int = Field(Query())
    name: str = Field(Query())

class EventsResponse(BaseModel):
    id: int = Field() #Field(Query(description="Event ID"))
    event_name: str = Field() #Field(Query(description="Title given by the LLM for the event"))
    start_date: Optional[datetime] = Field() #Field(Query(description="UTC timestamp for event start date"))
    end_date: Optional[datetime] = Field() #Field(Query(description="An UTC timestamp for event end date"))
    country: str = Field() #Field(Query())
    city: str = Field() #Field(Query())
    address: str = Field() #Field(Query())
    room: str = Field() #Field(Query())
    tags: List[Tag] = Field() #Field(Query())

    class Config:
        orm_mode = True
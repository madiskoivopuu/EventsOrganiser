import sys
sys.path.append('..')
from common import models, tables

import logging
logging.basicConfig(level=logging.INFO)
__logger = logging.getLogger(__name__)

from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime, tzinfo
from zoneinfo import ZoneInfo
from typing import Literal

from sqlalchemy import select, delete, update
from sqlalchemy import func
from sqlalchemy.orm import Session
import sqlalchemy.exc

import db

class ParsedEvent(BaseModel):
    event_name: str
    start_date: datetime | None
    end_date: datetime
    country: str
    city: str
    address: str
    room: str
    tags: list[str]

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def empty_str_to_none(cls, value: str) -> str | None:
        if(len(value) == 0):
            return None
        return value
    
    @model_validator(mode="after")
    def both_dates_not_none(self) -> "ParsedEvent":
        if(self.start_date == None and self.end_date == None):
            raise ValueError("Both start date and end date are empty, which is not allowed")
        return self

class NewEvents(BaseModel):
    user_id: str
    account_type: str
    mail_link: str
    events_timezone: ZoneInfo
    events: list[ParsedEvent]

def fix_and_combine_location(parsed_event: ParsedEvent) -> str:
    locations = []
    if(parsed_event.country != None and len(parsed_event.country)):
        locations.append(parsed_event.country.title())

    if(parsed_event.city != None and len(parsed_event.city)):
        locations.append(parsed_event.city.title())

    if(parsed_event.address != None and len(parsed_event.address)):
        locations.append(parsed_event.address)

    if(parsed_event.room != None and len(parsed_event.room)):
        locations.append(parsed_event.room)

    if(len(locations) == 0):
        return "N/A"
    else:
        return ", ".join(locations)

def get_or_create_tag(db_session: Session, tag_name: str) -> tables.TagsTable:
    query = select(tables.TagsTable) \
            .where(func.lower(tables.TagsTable.name) == tag_name.lower())
    tag_row = db_session.execute(query).scalar_one_or_none()

    if(tag_row == None):
        __logger.info(f"Creating new tag {tag_name} without committing, since it was missing")
        tag_row = tables.TagsTable()
        tag_row.name = tag_name

    return tag_row

def fix_datetimes(start_date: datetime | None, end_date: datetime, user_timezone: ZoneInfo) -> tuple[datetime | None, datetime]:
    """Returns fixed & localized UTC datetimes"""

    if(start_date == None):
        if(not models.tz_aware(end_date)):
            end_date = end_date.replace(tzinfo=user_timezone)
        return None, end_date

    # only one date has timezone defined, which is probably a weird AI issue so we extend the found timezone to the other datetime
    if(models.tz_aware(start_date) != models.tz_aware(end_date)):
        __logger.info("Found instance of only one (start_date, end_date) having timezone information provided by AI")
        __logger.info(f"{start_date=}, {end_date=}")

        defined_timezone: tzinfo = (start_date.tzinfo or end_date.tzinfo)
        if(not models.tz_aware(start_date)):
            start_date = start_date.replace(tzinfo=defined_timezone)
        else:
            end_date = end_date.replace(tzinfo=defined_timezone)
    elif(not models.tz_aware(start_date) and not models.tz_aware(end_date)):
        start_date = start_date.replace(tzinfo=user_timezone)
        end_date = end_date.replace(tzinfo=user_timezone)

    return start_date.astimezone(tz=ZoneInfo("UTC")), end_date.astimezone(tz=ZoneInfo("UTC"))

def validate_and_create_event_row(db_session: Session, parsed_event: ParsedEvent, user_timezone: ZoneInfo) -> tables.EventsTable:
    """Fixes a few AI related issues & returns a new events row object"""
    event_row = tables.EventsTable()
    event_row.event_name = parsed_event.event_name

    fixed_start_date_utc, fixed_end_date_utc = fix_datetimes(parsed_event.start_date, parsed_event.end_date, user_timezone)
    event_row.start_date_utc = fixed_start_date_utc
    event_row.end_date_utc = fixed_end_date_utc
    event_row.address = fix_and_combine_location(parsed_event)

    for tag_name in parsed_event.tags:
        event_row.tags.append(get_or_create_tag(db_session, tag_name))

    return event_row

def add_events_to_db(new_events: NewEvents) -> None:
    with db.start_session() as db_session:
        for parsed_event in new_events.events:
            try:
                event_row = validate_and_create_event_row(db_session, parsed_event, new_events.events_timezone)
            except ValueError:
                __logger.warning("Unexpected ValueError when validating event data, event dropped", exc_info=True)
                continue

            event_row.user_id = new_events.user_id
            event_row.user_acc_type = new_events.account_type
            event_row.email_link = new_events.mail_link
            db_session.add(event_row)

        db_session.commit()
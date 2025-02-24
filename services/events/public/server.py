from fastapi import Depends, FastAPI, Request, Response, HTTPException
from fastapi_pagination import Page, add_pagination, paginate
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate

import os, uuid

import icalendar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from datetime import timezone

import sys
sys.path.append('..')
from common import tables, models

import auth
from auth import UserData
import helpers
import db

api = FastAPI(debug=(os.getenv("DEV_MODE") == "1"))
add_pagination(api)

if(os.getenv("DEV_MODE") == "1"):
    from fastapi.middleware.cors import CORSMiddleware
    api.add_middleware(
        CORSMiddleware,
        allow_origins=['*']
    )

@api.get("/api/events")
async def get_events(
    request_data: models.EventsGetRequest = Depends(), # Required for the input parameters, so that FastAPI displays descriptions for query fields in Swagger
    user: UserData = Depends(auth.authenticate_user),
    db_session: AsyncSession = Depends(db.start_session)
) -> Page[models.EventsGetResponse]:
    """
    Authenticated API endpoint for listing events before or after a given date.
    The results are paginated in lists up to 100 events.
    """

    if(not models.tz_aware(request_data.from_time)):
        request_data.from_time = request_data.from_time.replace(tzinfo=timezone.utc)
    request_data.from_time = request_data.from_time.astimezone(timezone.utc) # NOTE: MySQL DATETIME comparision is done disregarding timezones, please always convert a non UTC datetime to an UTC one (since DATETIMEs in the database are stored as UTC)
 
    query = select(tables.EventsTable) \
            .where(
                tables.EventsTable.user_id == user.account_id, 
                tables.EventsTable.user_acc_type == user.account_type
            )
    if(request_data.direction == "forward"):
        query = query.where(tables.EventsTable.start_date_utc >= request_data.from_time)
    else:
        query = query.where(tables.EventsTable.end_date_utc < request_data.from_time)
        
    return await paginate(
        db_session,
        query
    )

@api.patch("/api/events/{id}", status_code=204)
async def update_event(
    id: int,
    new_data: models.EventsUpdateRequest,
    user: UserData = Depends(auth.authenticate_user),
    db_session: AsyncSession = Depends(db.start_session)
):
    """
    Authenticated API endpoint for updating event data
    """

    query = select(tables.EventsTable) \
            .where(
                tables.EventsTable.id == id,
                tables.EventsTable.user_id == user.account_id,
                tables.EventsTable.user_acc_type == user.account_type
            )
    
    query_result = await db_session.execute(query)
    event: tables.EventsTable = query_result.unique().scalar_one_or_none()
    if(event == None):
        raise HTTPException(status_code=404, detail=f"Event with id {id} not found")

    # new tags to replace old ones with
    tags_query = select(tables.TagsTable) \
                .filter(tables.TagsTable.name.in_(new_data.tags))
    tags_query_result = await db_session.execute(tags_query)

    event.event_name = new_data.event_name
    event.start_date_utc = new_data.start_date_utc
    event.end_date_utc = new_data.end_date_utc
    event.address = new_data.address
    event.tags = [tag for (tag, ) in tags_query_result.all()]
    
    await db_session.commit()

    return

@api.delete("/api/events/{id}", status_code=204)
async def delete_event(
    id: int,
    user: UserData = Depends(auth.authenticate_user),
    db_session: AsyncSession = Depends(db.start_session)
):
    """
    Authenticated API endpoint for deleting an event
    """

    query = delete(tables.EventsTable) \
            .where(
                tables.EventsTable.id == id,
                tables.EventsTable.user_id == user.account_id,
                tables.EventsTable.user_acc_type == user.account_type
            )
    
    query_result = await db_session.execute(query)
    await db_session.commit()

    if(query_result.rowcount == 0): # rowcount will be -1 for SQL db which will not support showing deleted rows
        raise HTTPException(status_code=404, detail=f"Event with id {id} not found")

    return

@api.get("/api/events/tags")
async def get_tags(
    db_session: AsyncSession = Depends(db.start_session)
) -> list[models.Tag]:
    """
    Unauthenticated API endpoint for fetching all available tags used for categorising events
    """
    query = select(tables.TagsTable)
    results = await db_session.execute(query)
    return results.scalars().all()



@api.get("/api/events/calendar/link")
async def get_link(
    request: Request,
    user: UserData = Depends(auth.authenticate_user),
    db_session: AsyncSession = Depends(db.start_session),
) -> models.CalendarLinkResponse:
    """
    Authenticated API endpoint for fetching the calendar link
    """

    query = select(tables.CalendarLinksTable) \
            .where(
                tables.CalendarLinksTable.user_id == user.account_id, 
                tables.CalendarLinksTable.user_acc_type == user.account_type
            )
    query_result = await db_session.execute(query)

    link_row = query_result.scalar_one_or_none()
    if(link_row == None):
        raise HTTPException(status_code=404, detail="No calendar link found")
    
    return models.CalendarLinkResponse(
        link=helpers.format_calendar_link(link_row.calendar_identifier, request)
    )

@api.post("/api/events/calendar/link")
async def generate_link(
    request: Request,
    user: UserData = Depends(auth.authenticate_user),
    db_session: AsyncSession = Depends(db.start_session),
) -> models.CalendarLinkResponse:
    """
    Authenticated API endpoint for creating or regenerating a calendar link
    """

    calendar_identifier = uuid.uuid4()

    query = select(tables.CalendarLinksTable) \
            .where(
                tables.CalendarLinksTable.user_id == user.account_id, 
                tables.CalendarLinksTable.user_acc_type == user.account_type
            )
    query_result = await db_session.execute(query)

    link_row = query_result.scalar_one_or_none()
    if(link_row != None):
        link_row.calendar_identifier = calendar_identifier
    else:
        row = tables.CalendarLinksTable(
            user_id=user.account_id,
            user_acc_type=user.account_type,
            calendar_identifier=calendar_identifier
        )
        db_session.add(row)

    await db_session.commit()

    return models.CalendarLinkResponse(
        link=helpers.format_calendar_link(calendar_identifier, request)
    )

@api.get("/api/events/calendar/{calendar_id}")
async def get_calendar_file(
    calendar_id: uuid.UUID,
    db_session: AsyncSession = Depends(db.start_session),
):
    """
    Unauthenticated API endpoint for converting found events to iCal format
    """
    
    calendar_query = select(tables.CalendarLinksTable) \
                    .where(tables.CalendarLinksTable.calendar_identifier == calendar_id)
    query_result = await db_session.execute(calendar_query)
    calendar_user = query_result.scalar_one_or_none()
    if(calendar_user == None):
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    query = select(tables.EventsTable) \
            .where(tables.EventsTable.user_id == calendar_user.user_id, tables.EventsTable.user_acc_type == calendar_user.user_acc_type) #\
    query_result = await db_session.stream(query)

    calendar: icalendar.Calendar = icalendar.Calendar()
    async for (event_row, ) in query_result.unique():
        calendar_event = icalendar.Event()
        calendar_event.add("NAME", event_row.event_name)
        calendar_event.add("DTSTART", event_row.start_date_utc.replace(tzinfo=timezone.utc))
        calendar_event.add("DTEND", event_row.end_date_utc.replace(tzinfo=timezone.utc))
        calendar_event.add("LOCATION", event_row.address) # TODO: handle empty string cases
        calendar_event.add("CATEGORIES", ", ".join([tag_row.name for tag_row in event_row.tags]))
        calendar.add_component(calendar_event)

    return Response(calendar.to_ical(), media_type="text/calendar")

@api.delete("/api/events/calendar/{calendar_id}", status_code=204)
async def delete_calendar_link(
    calendar_id: uuid.UUID,
    user: UserData = Depends(auth.authenticate_user),
    db_session: AsyncSession = Depends(db.start_session),
):
    """
    Authenticated API endpoint for deleting a calendar link for the user
    """

    query = delete(tables.CalendarLinksTable) \
            .where(
                tables.CalendarLinksTable.user_id == user.account_id, 
                tables.CalendarLinksTable.user_acc_type == user.account_type, 
                tables.CalendarLinksTable.calendar_identifier == calendar_id
            )
    query_result = await db_session.execute(query)
    await db_session.commit()

    if(query_result.rowcount == 0): # rowcount will be -1 for SQL db which will not support showing deleted rows
        raise HTTPException(status_code=404, detail="Calendar link not found")

    return
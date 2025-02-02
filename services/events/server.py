from fastapi import Depends, FastAPI, Request, Response, HTTPException
from fastapi_pagination import Page, add_pagination, paginate
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate

import os, pytz, uuid

import icalendar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from datetime import timezone

import server_config
import helpers
import db as db, tables
import models

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
    # session = ??
    db_session: AsyncSession = Depends(db.start_session)
) -> Page[models.EventsGetResponse]:
    """
    Authenticated API endpoint for listing events before or after a given date.
    The results are paginated in lists up to 100 events.
    """
    
    user_id = "aabb"
    acc_type = models.AccountType.OUTLOOK # TODO: in the future this data will be kept in session, since we do not allow multiple email accounts grouped into a single account on events organiser
                                            # TODO: also fetch the ID of the account type from database

    if(not models.tz_aware(request_data.from_time)):
        request_data.from_time = request_data.from_time.replace(tzinfo=pytz.UTC)
    request_data.from_time = request_data.from_time.astimezone(pytz.utc) # NOTE: MySQL DATETIME comparision is done disregarding timezones, please always convert a non UTC datetime to an UTC one (since DATETIMEs in the database are stored as UTC)
 
    query = select(tables.EventsTable).where(tables.EventsTable.user_id == user_id, tables.EventsTable.user_acc_type == acc_type)
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
    db_session: AsyncSession = Depends(db.start_session)
):
    """
    Authenticated API endpoint for updating event data
    """
    # TODO: replace with auth
    user_id = "aabb"
    acc_type = models.AccountType.OUTLOOK

    query = select(tables.EventsTable) \
            .where(tables.EventsTable.id == id,
                   tables.EventsTable.user_id == user_id,
                   tables.EventsTable.user_acc_type == acc_type)
    
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
    db_session: AsyncSession = Depends(db.start_session)
):
    # TODO: replace with auth
    user_id = "aabb"
    acc_type = models.AccountType.OUTLOOK

    query = delete(tables.EventsTable) \
            .where(tables.EventsTable.id == id,
                   tables.EventsTable.user_id == user_id,
                   tables.EventsTable.user_acc_type == acc_type)
    
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
    db_session: AsyncSession = Depends(db.start_session),
) -> models.CalendarLinkResponse:
    """
    Authenticated API endpoint for fetching the calendar link
    """
    # TODO: replace with auth
    user_id = "aabb"
    acc_type = models.AccountType.OUTLOOK

    query = select(tables.CalendarLinksTable) \
            .where(tables.CalendarLinksTable.user_id == user_id, tables.CalendarLinksTable.user_acc_type == acc_type)
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
    db_session: AsyncSession = Depends(db.start_session),
    # session = ??
) -> models.CalendarLinkResponse:
    """
    Authenticated API endpoint for creating or regenerating a calendar link
    """
    # TODO: replace with auth
    user_id = "aabb"
    acc_type = models.AccountType.OUTLOOK

    calendar_identifier = uuid.uuid4()

    query = select(tables.CalendarLinksTable) \
            .where(tables.CalendarLinksTable.user_id == user_id, tables.CalendarLinksTable.user_acc_type == acc_type)
    query_result = await db_session.execute(query)

    link_row = query_result.scalar_one_or_none()
    if(link_row != None):
        link_row.calendar_identifier = calendar_identifier
    else:
        row = tables.CalendarLinksTable(
            user_id=user_id,
            user_acc_type=acc_type,
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
    db_session: AsyncSession = Depends(db.start_session),
):
    """
    Authenticated API endpoint for deleting a calendar link for the user
    """

    # TODO: replace with auth
    user_id = "aabb"
    acc_type = models.AccountType.OUTLOOK

    query = delete(tables.CalendarLinksTable) \
            .where(tables.CalendarLinksTable.user_id == user_id, 
                   tables.CalendarLinksTable.user_acc_type == acc_type, 
                   tables.CalendarLinksTable.calendar_identifier == calendar_id)
    query_result = await db_session.execute(query)
    await db_session.commit()

    if(query_result.rowcount == 0): # rowcount will be -1 for SQL db which will not support showing deleted rows
        raise HTTPException(status_code=404, detail="Calendar link not found")

    return


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)
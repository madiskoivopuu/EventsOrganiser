from fastapi import Depends, FastAPI, Request, Response, HTTPException
from fastapi_pagination import Page, add_pagination, paginate
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate

import os, pytz, uuid

import icalendar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import timezone

import server_config
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
 
    query = select(tables.EventsTable).where(tables.EventsTable.mail_acc_id == user_id, tables.EventsTable.mail_acc_type == acc_type)
    if(request_data.direction == "forward"):
        query = query.where(tables.EventsTable.start_date >= request_data.from_time)
    else:
        query = query.where(tables.EventsTable.end_date < request_data.from_time)
        
    return await paginate(
        db_session,
        query
    )


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

@api.post("/api/events/calendar/regenerate")
async def generate_link(
    request: Request,
    db_session: AsyncSession = Depends(db.start_session),
    # session = ??
) -> models.GenerateCalendarLinkResponse:
    """
    Authenticated API endpoint for creating or regenerating a calendar link
    """
    user_id = "aabb"
    acc_type = models.AccountType.OUTLOOK

    calendar_identifier = uuid.uuid4()

    query = select(tables.CalendarLinksTable).where(tables.CalendarLinksTable.user_id == user_id, tables.CalendarLinksTable.user_acc_type == acc_type)
    query_result = await db_session.execute(query)

    prev_link_obj = query_result.scalar_one_or_none()
    if(prev_link_obj != None):
        prev_link_obj.calendar_identifier = calendar_identifier
    else:
        row = tables.CalendarLinksTable(
            user_id=user_id,
            user_acc_type=acc_type,
            calendar_identifier=calendar_identifier
        )
        db_session.add(row)

    await db_session.flush()
    await db_session.commit()

    calendar_link = str(request.url).replace(str(request.url.path), "") + "/api/events/calendar/" + str(calendar_identifier)

    return models.GenerateCalendarLinkResponse(
        link=calendar_link
    )

@api.get("/api/events/calendar/{calendar_id}")
async def get_calendar_file(
    calendar_id: uuid.UUID,
    db_session: AsyncSession = Depends(db.start_session),
):
    """Unauthenticated API endpoint for converting found events to iCal format"""
    
    calendar_query = select(tables.CalendarLinksTable) \
            .where(tables.CalendarLinksTable.calendar_identifier == calendar_id)
    query_result = await db_session.execute(calendar_query)
    calendar_user = query_result.scalar_one_or_none()
    if(calendar_user == None):
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    query = select(tables.EventsTable) \
            .where(tables.EventsTable.user_id == calendar_user.user_id, tables.EventsTable.user_acc_type == calendar_user.user_acc_type) \
            .limit(100) # TODO: remove lol
            #.options(selectinload(tables.EventsTable.tags)) \
            #.execution_options(yield_per=server_config.YIELD_EVENTS_PER_TIME)
    query_result = await db_session.execute(query)

    calendar: icalendar.Calendar = icalendar.Calendar()
    for event in query_result.unique().scalars().yield_per(10):
        # TODO: separate function for this, would fix other todos aswell
        calendar_event = icalendar.Event()
        calendar_event.add("NAME", event.event_name)
        calendar_event.add("DTSTART", event.start_date_utc.replace(tzinfo=timezone.utc))
        calendar_event.add("DTEND", event.end_date_utc.replace(tzinfo=timezone.utc))
        calendar_event.add("LOCATION", ", ".join([event.country, event.city, event.address, event.room])) # TODO: handle empty string cases
        #TODO: tags, categorisation
        calendar.add_component(calendar_event)

    return Response(calendar.to_ical(), media_type="text/calendar")

'''@api.post("/internal/api/events", status_code=201)
async def add_event(
    event_data: models.EventPostRequest,
    db_session: AsyncSession = Depends(db.start_session)
):
    """
    Internal API for adding events for a user.
    """

    event_model_sql = tables.EventsTable(
        mail_acc_type=event_data.mail_acc_type,
        mail_acc_id=event_data.mail_acc_id,
        event_name=event_data.event_name,
        start_date=event_data.start_date,
        end_date=event_data.end_date,
        country=event_data.country,
        city=event_data.city,
        address=event_data.address,
        room=event_data.room
    )

    for tag in event_data.tags:
        event_model_sql.tags.append(
            tables.TagsTable(name=tag)
        )

    db_session.add(event_model_sql)
    await db_session.commit()
    return None'''


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)
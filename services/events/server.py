from fastapi import Depends, FastAPI, Request, status, Query
from fastapi_server_session import SessionManager, MongoSessionInterface, Session
from fastapi_pagination import Page, add_pagination, paginate
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate

import os, pytz

import pymongo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import server_config
import apps
import db as db, tables
import models

session_manager = SessionManager(
    interface=MongoSessionInterface(
        pymongo.MongoClient(
            server_config.SESSION_MONGODB_HOST,
            username=server_config.SESSION_MONGODB_USER,
            password=server_config.SESSION_MONGODB_PASSWORD,
            authSource=server_config.SESSION_MONGODB_DB
        ),
        db=server_config.SESSION_MONGODB_DB,
        collection="session",
    )
)



api = FastAPI(debug=True)
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
    session: Session = Depends(session_manager.use_session),
    db_session: AsyncSession = Depends(db.start_session)
) -> Page[models.EventsGetResponse]:
    """
    Authenticated API endpoint for listing events before or after a given date.
    The results are paginated in lists up to 100 events.
    """

    ms = apps.get_ms_app(session)
    if(ms.get_user() == None):
        return JSONResponse(
            content={"status": "error", "message": "User is not authenticated"},
            status_code=403
        )
    
    user_id = ms.get_user()["oid"]
    acc_type = 1 # TODO: in the future this data will be kept in session, since we do not allow multiple email accounts grouped into a single account on events organiser
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

@api.post("/internal/api/events", status_code=201)
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
    return None


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)
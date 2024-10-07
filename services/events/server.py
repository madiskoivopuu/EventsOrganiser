import asyncio
from datetime import datetime

from fastapi import Depends, FastAPI, Request, status, Query
from fastapi.responses import JSONResponse
from fastapi_server_session import SessionManager, MongoSessionInterface, Session
from fastapi_pagination import Page, add_pagination, paginate
from fastapi_pagination.ext.sqlalchemy import paginate

import pytz

import pymongo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from typing import Annotated

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

# DEV mode - sometimes there is an event loop running, other times there isn't; looks like this has something to do with the hot reloader?
try:
    loop = asyncio.get_running_loop()
    loop.create_task(tables.create_tables())
except RuntimeError:
    asyncio.run(tables.create_tables())

# Based on https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive , checks if datetime object knows what timezone it is in
def tz_aware(dt):
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None

@api.get("/api/events")
async def get_events(
    request_data: models.EventsRequest = Depends(),
    session: Session = Depends(session_manager.use_session),
    db_session: AsyncSession = Depends(db.start_session)
) -> Page[models.EventsResponse]:
    """ms = apps.get_ms_app(session)
    if(ms.get_user() == None):
        return JSONResponse(
            content={"status": "error", "message": "User is not authenticated"},
            status_code=403
        )
    
    user_id = ms.get_user()["oid"]"""
    if(not tz_aware(request_data.from_time)):
        request_data.from_time = request_data.from_time.replace(tzinfo=pytz.UTC)

    user_id = "aabb"
    acc_type = 1 # TODO: in the future this data will be kept in session, since we do not allow multiple email accounts grouped into a single account on events organiser
                 # TODO: also fetch the ID of the account type from database

    query = select(tables.EventsTable).where(tables.EventsTable.mail_acc_id == user_id, tables.EventsTable.mail_acc_type == acc_type)
    if(request_data.direction == "forward"):
        query = query.where(tables.EventsTable.start_date >= request_data.from_time)
    else:
        query = query.where(tables.EventsTable.end_date < request_data.from_time)
        
    return await paginate(
        db_session,
        query
    )

@api.post("/api/events")
async def add_event():
    pass

@api.get("/api/events/tags")
async def get_tags():
    pass



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)
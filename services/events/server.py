from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi_server_session import SessionManager, MongoSessionInterface, Session
import pymongo
from datetime import datetime

import server_config
import apps

import sql, tables

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

api = FastAPI()

@api.middleware("http")
async def verify_authentication(request: Request, call_next, session: Session = Depends(session_manager.use_session)):
    ms = apps.get_ms_app(session)
    if(ms.get_user() == None):
        return JSONResponse(
            content={"status": "error", "message": "User is not authenticated"},
            status_code=403
        )
    
    response = await call_next(request)
    return response

@api.get("/api/events")
async def get_events(
    start_date: datetime | None, 
    end_date: datetime | None, 
    session: Session = Depends(session_manager.use_session)
):
    ms = apps.get_ms_app(session)
    user = ms.get_user()



    return {"status": "ok"}

@api.get("/get")
async def get_session(session: Session = Depends(session_manager.use_session)):
    print(session["_auth_flow"])
    return {"value": session["_auth_flow"]}

api.add_middleware(verify_authentication)
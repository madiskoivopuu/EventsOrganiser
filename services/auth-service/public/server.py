from fastapi import Depends, FastAPI, Request, Response, HTTPException
from fastapi_pagination import Page, add_pagination, paginate
from fastapi.responses import JSONResponse
from fastapi_pagination.ext.sqlalchemy import paginate

import os

from routes import microsoft_router

api = FastAPI(
    debug=(os.getenv("DEV_MODE") == "1")
)
api.include_router(microsoft_router)
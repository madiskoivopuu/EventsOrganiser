#import sys
#sys.path.append('..')


from contextlib import asynccontextmanager
from fastapi import FastAPI
from mq.notifications import NotifiactionMQ

import os, server_config
from routes import settings_router, emails_router

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    user_listener = NotifiactionMQ(
        host=server_config.RABBITMQ_HOST,
        virtual_host=server_config.RABBITMQ_VIRTUALHOST,
        username=server_config.RABBITMQ_USERNAME,
        password=server_config.RABBITMQ_PASSWORD
    ) 

    yield

    # cleanup
    user_listener.close_conn()

api = FastAPI(
    debug=(os.getenv("DEV_MODE") == "1"),
    lifespan=app_lifespan
)

api.include_router(settings_router)
api.include_router(emails_router)
import app_config
import pymongo
import identity
from flask import session

__MS_APP = None
__MONGO_CON = None

def get_ms_app():
    if __MS_APP == None:
        __MS_APP = identity.web.Auth(
            session=session,
            authority="https://login.microsoftonline.com/common",
            client_id=app_config.MICROSOFT_APP_CLIENT_ID,
            client_credential=app_config.MICROSOFT_APP_SECRET
        )

    return __MS_APP

def get_mongo_connection():
    if __MONGO_CON == None:
        __MONGO_CON = pymongo.MongoClient(app_config.SESSION_MONGODB_HOST,
                                            username=app_config.SESSION_MONGODB_FLASK_USER,
                                            password=app_config.SESSION_MONGODB_FLASK_PASSWORD,
                                            authSource=app_config.SESSION_MONGODB_FLASK_DB
                                          )
        
    return __MONGO_CON
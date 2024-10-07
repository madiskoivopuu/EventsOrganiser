import os, dotenv
dotenv.load_dotenv() # only for local testing, the docker container will already have environment variables set for it

MICROSOFT_APP_CLIENT_ID = os.getenv("MICROSOFT_APP_CLIENT_ID")
MICROSOFT_APP_SECRET = os.getenv("MICROSOFT_APP_SECRET")

SESSION_MONGODB_HOST = "172.17.89.147:27017"
SESSION_MONGODB_USER = "session_manager"
SESSION_MONGODB_PASSWORD = os.getenv("MONGODB_FLASK_PASSWORD")
SESSION_MONGODB_DB = "sessions"

MYSQL_EVENTS_USER = os.getenv("MYSQL_EVENTS_USER")
MYSQL_EVENTS_PASSWORD = os.getenv("MYSQL_EVENTS_PASSWORD")

LIMIT_RESULTS = 100
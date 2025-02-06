import os, dotenv
dotenv.load_dotenv() # only for local testing, the docker container will already have environment variables set for it

MICROSOFT_APP_CLIENT_ID = os.getenv("MICROSOFT_APP_CLIENT_ID")
MICROSOFT_APP_SECRET = os.getenv("MICROSOFT_APP_SECRET")

REDIS_HOST_URL = os.getenv("REDIS_HOST_URL")
JWT_SECRET = os.getenv("JWT_SECRET")

MICROSOFT_SCOPES=["api://e7531514-8913-47a8-8cd2-b80dcef955b7/emails"]


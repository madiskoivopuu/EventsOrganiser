import os, dotenv
dotenv.load_dotenv() # only for local testing, the docker container will already have environment variables set for it

MICROSOFT_APP_CLIENT_ID = os.getenv("MICROSOFT_APP_CLIENT_ID")
MICROSOFT_APP_SECRET = os.getenv("MICROSOFT_APP_SECRET")
MICROSOFT_SCOPES=["Mail.Read"]

REDIS_HOST_URL = os.getenv("REDIS_HOST_URL")

RABBITMQ_EMAILS_QUEUE = os.getenv("RABBITMQ_EMAILS_QUEUE")
RABBITMQ_USERS_QUEUE = os.getenv("RABBITMQ_USERS_QUEUE")

JWT_SECRET = os.getenv("JWT_SECRET")
if(os.getenv("DEV_MODE") == "1"):
    JWT_SESSION_COOKIE_NAME = "session-jwt"
else:
    JWT_SESSION_COOKIE_NAME = "__Secure-session-jwt"
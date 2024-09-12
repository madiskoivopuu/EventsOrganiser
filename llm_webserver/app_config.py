import os, dotenv
dotenv.load_dotenv()

MICROSOFT_APP_CLIENT_ID = os.getenv("MICROSOFT_APP_CLIENT_ID")
MICROSOFT_APP_SECRET = os.getenv("MICROSOFT_APP_SECRET")

EVENTS_PARSER_MYSQL_USER = "events_parser"
EVENTS_PARSER_MYSQL_PASSWORD = os.getenv("EVENTS_PARSER_MYSQL_PASSWORD")

# Tells the Flask-session extension to store sessions in the filesystem
SESSION_TYPE = "filesystem"
# TODO: mysql db to hold sessions, maybe a local db even
# Using the file system will not work in most production systems,
# it's better to use a database-backed session store instead.
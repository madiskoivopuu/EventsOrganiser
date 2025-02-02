import uuid
from fastapi import Request

def format_calendar_link(calendar_identifier: uuid.UUID, request: Request):
    host = str(request.url).replace(str(request.url.path), "")
    return host + "/api/events/calendar/" + str(calendar_identifier)
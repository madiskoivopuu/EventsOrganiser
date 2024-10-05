import identity.web
import server_config
from fastapi_server_session import Session

def get_ms_app(session: Session):
    ms = identity.web.Auth(
        session=session,
        authority="https://login.microsoftonline.com/common",
        client_id=server_config.MICROSOFT_APP_CLIENT_ID,
        client_credential=server_config.MICROSOFT_APP_SECRET
    )
    return ms
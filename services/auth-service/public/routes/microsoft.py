from fastapi import APIRouter, Request
import msal
import identity.web
identity.web.Auth

import server_config

ms_app = msal.ConfidentialClientApplication(
    client_id=server_config.MICROSOFT_APP_CLIENT_ID,
    client_credential=server_config.MICROSOFT_APP_SECRET
)
microsoft_router = APIRouter(
    prefix="/api/auth/microsoft"
)

def get_redirect_uri(request: Request):
    pass

@microsoft_router.post("/")
def get_login_link(
    request
):
    ms_app.initiate_auth_code_flow(
        scopes=server_config.MICROSOFT_SCOPES
    )

    pass
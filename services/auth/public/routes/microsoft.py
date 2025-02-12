from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi_server_session import Session, SessionManager, AsyncRedisSessionInterface
from redis import asyncio as aioredis
from datetime import timedelta
from zoneinfo import ZoneInfo
import msal
import aiohttp
import certifi, ssl
sslcontext = ssl.create_default_context(cafile=certifi.where())
import logging
logging.basicConfig(level=logging.INFO)

import server_config
from helpers import auth

__logger = logging.getLogger(__name__)
microsoft_router = APIRouter(
    prefix="/api/auth/microsoft"
)
session_manager = SessionManager(
    default_sess_duration=timedelta(minutes=10),
    interface=AsyncRedisSessionInterface(
        redis_client=aioredis.from_url(server_config.REDIS_HOST_URL)
    )
)
ms_app = msal.ConfidentialClientApplication(
    client_id=server_config.MICROSOFT_APP_CLIENT_ID,
    client_credential=server_config.MICROSOFT_APP_SECRET
)

def get_redirect_uri(request: Request):
    host = str(request.url).replace(str(request.url.path), "")
    return host + "/api/auth/microsoft/login_callback"

async def get_ms_signing_keys() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get('https://login.microsoftonline.com/common/discovery/v2.0/keys', ssl=sslcontext) as response:
            resp_json = await response.json()
            return resp_json
        
@microsoft_router.post("/")
async def get_login_link(
    #timezone: ZoneInfo,
    request: Request,
    session: Session = Depends(session_manager.get_or_start_session)
) -> str:
    
    flow = ms_app.initiate_auth_code_flow(
        scopes=server_config.MICROSOFT_SCOPES,
        redirect_uri=get_redirect_uri(request),
    )
    session["ms_flow"] = flow
    #session["specified_timezone"] = timezone # used for first login to properly create settings...

    return flow["auth_uri"]

@microsoft_router.get("/login_callback")
async def finish_login(
    request: Request,
    response: Response,
    session: Session = Depends(session_manager.get_session)
):
    if(session == None):
        raise HTTPException(status_code=400, detail="Auth flow not initiated prior to this request")
    
    auth_flow = ms_app.acquire_token_by_auth_code_flow(auth_code_flow=session["ms_flow"], auth_response=dict(request.query_params))
    if "error" in auth_flow:
        error_str = auth_flow["error_description"] if "error_description" in auth_flow else auth_flow["error"]
        raise HTTPException(status_code=400, detail=f"Problem authenticating with Microsoft account: {error_str}")

    print(auth_flow)

    signing_keys = await get_ms_signing_keys()
    decoded_token, err_msg = auth.decode_jwt_token(auth_flow["id_token"], signing_keys, server_config.MICROSOFT_APP_CLIENT_ID)
    if(decoded_token == None):
        __logger.warning(f"Problem decoding JWT token after Microsoft login callback: {err_msg}")
        raise HTTPException(status_code=400, detail=f"Unable to verify that the response token is issued by Microsoft")

    token_data = auth.create_jwt_from_microsoft(decoded_token, server_config.JWT_SECRET)
    auth.set_jwt_cookie(server_config.JWT_SESSION_COOKIE_NAME, token_data, response)

    # TODO: user logged in noti

    return
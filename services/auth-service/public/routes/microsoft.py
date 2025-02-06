from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi_server_session import Session, SessionManager, AsyncRedisSessionInterface
from redis import asyncio as aioredis
from datetime import timedelta
import msal
import aiohttp

import server_config
from helpers import auth

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
        async with session.get('https://login.microsoftonline.com/common/discovery/v2.0/keys') as response:
            resp_json = await response.json()
            return resp_json
        
@microsoft_router.post("/")
async def get_login_link(
    request: Request,
    session: Session = Depends(session_manager.get_or_start_session)
) -> str:
    
    flow = ms_app.initiate_auth_code_flow(
        scopes=server_config.MICROSOFT_SCOPES,
        redirect_uri=get_redirect_uri(request)
    )
    session["ms_flow"] = flow

    return flow["auth_uri"]

@microsoft_router.get("/login_callback")
async def finish_login(
    request: Request,
    session: Session = Depends(session_manager.get_session)
):
    if(session == None):
        raise HTTPException(status_code=400, detail="Auth flow not initiated prior to this request")
    
    resp = ms_app.acquire_token_by_auth_code_flow(auth_code_flow=session["ms_flow"], auth_response=dict(request.query_params))
    if "error" in resp:
        error_str = resp["error_description"] if "error_description" in resp else resp["error"]
        raise HTTPException(status_code=400, detail=f"Problem authenticating with Microsoft account: {error_str}")

    signing_keys = await get_ms_signing_keys()
    if(not auth.decode_jwt_token(resp["id_token"], signing_keys)):
        pass

    return
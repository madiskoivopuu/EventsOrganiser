import aiohttp
import jwt
from datetime import datetime, timezone, timedelta

class TokenUpdateError(Exception):
    pass

import certifi, ssl
sslcontext = ssl.create_default_context(cafile=certifi.where())

async def update_token_if_needed(
        access_token: str, 
        expires_at: datetime,
        refresh_token: str, 
        client_id: str,
        client_secret: str,
        scopes: list[str],
        tenant: str = "common",
        if_expires_in_less_than: timedelta = timedelta(minutes=5)) -> tuple[str, datetime] | None:
    """
    Exchanges a refresh token for a new Microsoft access token, if the current one is about to expire

    :raises TokenUpdateError: If the response does not indicate that the refresh token has expired, but the response was erroneous (status code != 200)

    :return: None if the token has expired and it cannot be updated. Otherwise, a tuple of the token (old if no update was needed) and the expiration time
    """
    if(expires_at - datetime.now(timezone.utc) < if_expires_in_less_than):
        async with aiohttp.ClientSession("https://login.microsoftonline.com") as session:
            async with session.post(
                f"/{tenant}/oauth2/v2.0/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={
                    "client_id": client_id,
                    "scope": " ".join(scopes),
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_secret": client_secret
                }) as resp:
                    resp_text = await resp.text()

                    if(resp.status == 200):
                        resp_data = await resp.json()
                        return (resp_data["access_token"], datetime.now(timezone.utc) + timedelta(seconds=resp_data["expires_in"]))
                    elif(resp.status == 400):
                        # check for an error that says that the refresh token has expired
                        resp_data = await resp.json()

                        if(50173 in resp_data["error_codes"]):
                            return None

                        raise TokenUpdateError(f"Received 'Bad request' error trying to update token. Response: {resp_text}")
                    else:
                        raise TokenUpdateError(f"Received status code {resp.status} trying to update the token. Response: {resp_text}")
    else:
        return (access_token, expires_at)

async def get_messages(access_token: str, select: list | None, skip: int = 0, top: int = 100) -> dict:
    """
    Gets emails of a user from Microsoft Graph API
    
    :return: a dictionary containing
        "resp" - the response object,
        "json_data" - response body as json
    """
    params = {
        "$top": top,
        "$skip": skip
    }
    if(select):
        params["$select"] = ",".join(select)

    async with aiohttp.ClientSession("https://graph.microsoft.com/v1.0/") as session:
        async with session.get(
                "/me/messages", 
                params=params,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Prefer": 'outlook.body-content-type="text"'
                }, ssl=sslcontext) as resp:
            resp_json = await resp.json()

            return {
                "resp": resp,
                "json_data": resp_json
            }

async def get_message(id: str, access_token: str, select: list | None) -> dict:
    """
    Gets the contents of a single email for a user from Microsoft Graph API

    :return: a dictionary containing
        "resp" - the response object,
        "json_data" - response body as json
    """
    params = {}
    if(select):
        params["$select"] = ",".join(select)

    async with aiohttp.ClientSession("https://graph.microsoft.com/v1.0/") as session:
        async with session.get(
                f"/me/messages/{id}", 
                params=params,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Prefer": 'outlook.body-content-type="text"'
                }) as resp:
            resp_json = await resp.json()

            return {
                "resp": resp,
                "json_data": resp_json
            }

async def read_emails_after_date(
        access_token: str, 
        after_date: datetime | None, 
        select: list | None,
        skip: int = 0, 
        top: int = 100) -> dict:
    """
    Fetches emails for a Microsoft user after a specified UTC time
    
    Returns the emails that the user received after "after_date"
    """
    emails = []
    if("sentDateTime" not in select):
        select.append("sentDateTime")

    if(after_date == None):
        after_date = datetime.now(timezone.utc) - timedelta(days=31)

    while True:
        result = await get_messages(access_token, select=select, skip=skip, top=top)
        if(len(result["json_data"]["data"]["value"]) == 0): # no more emails to read from user
            break
        
        added_emails = 0
        for email in result["data"]["value"]:
            if(datetime.fromisoformat(email["sentDateTime"]) <= after_date):
                continue

            emails.append(email)

        if(added_emails == 0): # none found after date
            break

        skip += top

    return emails
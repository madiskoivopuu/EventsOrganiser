from fastapi import Request, HTTPException
from datetime import timedelta
from pydantic import BaseModel, Field
import jwt, jwt.exceptions

class UserData(BaseModel):
    email: str = Field(alias="sub")
    account_type: str
    account_id: str

async def authenticate_user(cookie_name: str, secret: str, request: Request) -> UserData:
    """
    Authenticates a user based on the session cookie contained JWT token.

    Raises:
        HTTPException when JWT fails validation.

    Returns:
        Returns the JWT data if it is valid.
    """
    val = request.cookies.get(cookie_name)
    if(val == None):
        raise HTTPException(status_code=401, detail="This endpoint requires authentication")
    
    try:
        decoded = jwt.decode(
            jwt=val,
            key=secret,
            leeway=timedelta(seconds=10)
        )
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    return UserData.model_validate(decoded)
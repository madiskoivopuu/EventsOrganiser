import jwt, jwt.exceptions
from fastapi import Response
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from enum import Enum

def decode_jwt_token(id_token: str, keys: dict, audience: str) -> tuple[dict | None, str]:
    """Verifies that a JWT is signed by a valid (trusted) public key. Decodes the token

       Returns the decoded token if it is valid, otherwise None and an error message
    """
    header = jwt.get_unverified_header(id_token)
    decrypt_key = None
    for key in keys["keys"]:
        if(key["kid"] == header["kid"]):
            decrypt_key = key
            break
    if(decrypt_key == None):
        return None, f"Key {header['kid']} not found in Microsoft Entra tenant-independent key endpoint"
    
    try:
        decoded = jwt.decode(
            jwt=id_token,
            key=jwt.PyJWK.from_dict(decrypt_key),
            algorithms=["RS256"],
            audience=audience
        )
    except jwt.exceptions.ExpiredSignatureError as e:
        return None, f"JWT token is expired ({e})"
    except jwt.exceptions.InvalidTokenError as e:
        return None, f"Unable to decode token due to some issue ({e})"
    return decoded, ""

def create_jwt_from_microsoft(id_token_data: dict, secret: str, expiration: timedelta = timedelta(minutes=30)) -> str:
    """Creates a JWT token from Microsoft's id_token data"""
    data = {}
    data["account_id"] = id_token_data["oid"]
    data["account_type"] = "outlook"
    # metadata
    data["sub"] = id_token_data["email"]
    data["exp"] = datetime.now(timezone.utc) + expiration

    return jwt.encode(
        data, 
        secret
    )

def set_jwt_cookie(name: str, value: str, response: Response, expiration: timedelta = timedelta(minutes=30)):
    """Puts a Set-Cookie header in the HTTP response to carry the JWT"""
    response.set_cookie(
        key=name,
        value=value,
        httponly=True,
        secure=True,
        max_age=expiration.total_seconds()
    )
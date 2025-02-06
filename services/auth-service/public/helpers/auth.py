import jwt, jwt.exceptions

def decode_jwt_token(id_token: str, keys: dict, audience: str) -> tuple[dict, str]:
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
    except jwt.exceptions.InvalidTokenError:
        return None, f"Unable to decode token due to some issue"
    return decoded, ""
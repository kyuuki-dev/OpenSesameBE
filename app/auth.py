
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer
from jose import jwt
import requests
import os

security = HTTPBearer()
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")

def get_token_auth_header(request: Request = Depends(security)):
    return request.credentials

def verify_jwt(token: str = Depends(get_token_auth_header)):
    try:
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        jwks = requests.get(jwks_url).json()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Unable to find appropriate key")
        payload = jwt.decode(token, rsa_key, algorithms=["RS256"], audience=AUTH0_AUDIENCE, issuer=f"https://{AUTH0_DOMAIN}/")
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

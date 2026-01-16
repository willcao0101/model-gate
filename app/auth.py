from fastapi import Header, HTTPException
from .settings import settings

def require_token(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing Bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    if token != settings.gateway_token:
        raise HTTPException(403, "Invalid token")

"""JWT authentication for the connector API. Never trust client-supplied user IDs."""
import uuid
from collections.abc import AsyncGenerator
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_session

bearer = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


@lru_cache(maxsize=1)
def _jwks_client() -> PyJWKClient:
    if not settings.supabase_url:
        raise RuntimeError("SUPABASE_URL is required for JWT authentication")
    return PyJWKClient(
        settings.supabase_url.rstrip("/") + "/auth/v1/.well-known/jwks.json",
        cache_jwk_set=True,
        lifespan=300,
        timeout=5,
    )


def verify_access_token(token: str) -> uuid.UUID:
    """Validate Supabase asymmetric JWT; fail closed on missing configuration."""
    if not settings.supabase_url:
        raise HTTPException(status_code=503, detail="Authentication not configured")
    try:
        key = _jwks_client().get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256", "ES256"],
            audience=settings.supabase_jwt_audience,
            issuer=settings.supabase_url.rstrip("/") + "/auth/v1",
            options={"require": ["exp", "iat", "sub", "aud", "iss"]},
            leeway=30,
        )
        if payload.get("role") != "authenticated":
            raise jwt.InvalidTokenError("Invalid role")
        return uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc


async def get_current_user_id(
    authorization: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> uuid.UUID:
    if authorization is None or authorization.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Bearer token required")
    return verify_access_token(authorization.credentials)

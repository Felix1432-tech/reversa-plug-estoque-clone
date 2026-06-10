import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


async def get_current_user_id(
    x_user_id: str = Header(..., description="User ID (UUID) — will be replaced by JWT auth"),
) -> uuid.UUID:
    """Temporary auth: extract user_id from header.
    TODO: Replace with JWT token validation from Supabase auth.
    """
    try:
        return uuid.UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID")

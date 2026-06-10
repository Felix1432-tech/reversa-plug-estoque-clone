import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base


@pytest.fixture(scope="session")
def encryption_key() -> str:
    return Fernet.generate_key().decode()


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def sample_credentials() -> dict:
    return {"login": "test@example.com", "password": "test123"}

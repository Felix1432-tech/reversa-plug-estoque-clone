"""Fail-closed authentication tests; no Supabase or DPK network calls."""
import uuid
from unittest.mock import patch

import jwt
import pytest
from fastapi import HTTPException

from app.api.deps import get_current_user_id, verify_access_token
from fastapi.security import HTTPAuthorizationCredentials


@pytest.mark.asyncio
async def test_missing_bearer_rejected():
    with pytest.raises(HTTPException) as exc:
        await get_current_user_id(None)
    assert exc.value.status_code == 401


def test_missing_configuration_rejected():
    with patch("app.api.deps.settings.supabase_url", ""):
        with pytest.raises(HTTPException) as exc:
            verify_access_token("untrusted")
    assert exc.value.status_code == 503


def test_forged_token_rejected():
    with patch("app.api.deps.settings.supabase_url", "https://example.supabase.co"), \
         patch("app.api.deps._jwks_client") as jwks:
        jwks.return_value.get_signing_key_from_jwt.side_effect = jwt.InvalidTokenError("bad")
        with pytest.raises(HTTPException) as exc:
            verify_access_token("forged")
    assert exc.value.status_code == 401

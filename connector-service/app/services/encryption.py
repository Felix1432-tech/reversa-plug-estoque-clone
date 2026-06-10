import json

from cryptography.fernet import Fernet, InvalidToken

from app.config import settings


class EncryptionService:
    def __init__(self, key: str | None = None):
        self._fernet = Fernet(key or settings.encryption_key)

    def encrypt(self, data: dict) -> bytes:
        payload = json.dumps(data).encode("utf-8")
        return self._fernet.encrypt(payload)

    def decrypt(self, token: bytes) -> dict:
        try:
            payload = self._fernet.decrypt(token)
            return json.loads(payload.decode("utf-8"))
        except InvalidToken as exc:
            raise ValueError("Failed to decrypt credentials: invalid key or corrupted data") from exc


encryption_service = EncryptionService()

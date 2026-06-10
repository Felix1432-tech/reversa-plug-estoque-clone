import pytest
from cryptography.fernet import Fernet

from app.services.encryption import EncryptionService


@pytest.fixture
def svc(encryption_key: str) -> EncryptionService:
    return EncryptionService(key=encryption_key)


def test_encrypt_decrypt_roundtrip(svc: EncryptionService):
    data = {"login": "user@test.com", "password": "s3cret!"}
    encrypted = svc.encrypt(data)
    decrypted = svc.decrypt(encrypted)
    assert decrypted == data


def test_encrypted_data_differs_from_plaintext(svc: EncryptionService):
    data = {"login": "user@test.com", "password": "s3cret!"}
    encrypted = svc.encrypt(data)
    assert b"s3cret" not in encrypted
    assert b"user@test.com" not in encrypted


def test_decrypt_with_wrong_key_raises(svc: EncryptionService):
    data = {"login": "x", "password": "y"}
    encrypted = svc.encrypt(data)

    wrong_key = Fernet.generate_key().decode()
    wrong_svc = EncryptionService(key=wrong_key)

    with pytest.raises(ValueError, match="Failed to decrypt"):
        wrong_svc.decrypt(encrypted)


def test_encrypt_produces_bytes(svc: EncryptionService):
    encrypted = svc.encrypt({"a": 1})
    assert isinstance(encrypted, bytes)

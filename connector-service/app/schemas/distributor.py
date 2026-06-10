import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CredentialsInput(BaseModel):
    login: str
    password: str


class DistributorCreate(BaseModel):
    distributor_type: str = Field(
        ...,
        pattern=r"^(dpk|furacao|rufato|isapa|pellegrino|laquila|rolemarmaster)$",
    )
    credentials: CredentialsInput
    settings: dict = Field(default_factory=dict)


class DistributorUpdate(BaseModel):
    credentials: CredentialsInput | None = None
    settings: dict | None = None


class DistributorResponse(BaseModel):
    id: uuid.UUID
    distributor_type: str
    status: str
    last_sync_at: datetime | None = None
    last_error: str | None = None
    settings: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestConnectionResponse(BaseModel):
    status: str
    message: str


class RunConnectorResponse(BaseModel):
    log_id: uuid.UUID
    status: str

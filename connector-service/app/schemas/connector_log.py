import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ConnectorLogResponse(BaseModel):
    id: uuid.UUID
    distributor_config_id: uuid.UUID
    started_at: datetime
    finished_at: datetime | None = None
    status: str
    products_found: int = 0
    products_created: int = 0
    products_updated: int = 0
    errors_count: int = 0
    error_details: list = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ConnectorLogListResponse(BaseModel):
    items: list[ConnectorLogResponse]
    total: int

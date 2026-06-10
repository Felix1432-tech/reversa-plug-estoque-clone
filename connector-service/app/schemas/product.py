import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductResponse(BaseModel):
    id: uuid.UUID
    distributor_config_id: uuid.UUID
    sku: str
    name: str
    description: str | None = None
    price: Decimal | None = None
    stock_quantity: int | None = None
    weight: Decimal | None = None
    height: Decimal | None = None
    width: Decimal | None = None
    length: Decimal | None = None
    photos: list[str] = Field(default_factory=list)
    fiscal_data: dict = Field(default_factory=dict)
    status: str
    last_stock_check_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    limit: int
    offset: int

import uuid
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user_id
from app.repositories.distributor_repo import DistributorRepository
from app.repositories.product_repo import ProductRepository
from app.schemas.product import ProductListResponse, ProductResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    distributor_type: str | None = Query(None),
    status: str | None = Query(None),
    search: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    dist_repo = DistributorRepository(db)
    configs = await dist_repo.list_by_user(user_id)

    if distributor_type:
        configs = [c for c in configs if c.distributor_type == distributor_type]

    config_ids = [c.id for c in configs]
    if not config_ids:
        return ProductListResponse(items=[], total=0, limit=limit, offset=offset)

    product_repo = ProductRepository(db)
    items, total = await product_repo.list_products(
        user_distributor_ids=config_ids,
        status=status,
        search=search,
        limit=limit,
        offset=offset,
    )

    return ProductListResponse(
        items=[ProductResponse.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
    )

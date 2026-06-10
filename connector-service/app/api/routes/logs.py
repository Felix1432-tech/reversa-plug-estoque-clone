import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user_id
from app.repositories.distributor_repo import DistributorRepository
from app.repositories.log_repo import LogRepository
from app.schemas.connector_log import ConnectorLogResponse, ConnectorLogListResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("", response_model=ConnectorLogListResponse)
async def list_logs(
    distributor_id: uuid.UUID | None = Query(None),
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    dist_repo = DistributorRepository(db)
    log_repo = LogRepository(db)

    if distributor_id:
        config = await dist_repo.get_by_id(distributor_id, user_id)
        if not config:
            raise HTTPException(status_code=404, detail="Distribuidor não encontrado")
        items, total = await log_repo.list_by_distributor(distributor_id, limit, offset)
    else:
        configs = await dist_repo.list_by_user(user_id)
        config_ids = [c.id for c in configs]
        if not config_ids:
            return ConnectorLogListResponse(items=[], total=0)
        items, total = await log_repo.list_by_user_distributors(config_ids, limit, offset)

    return ConnectorLogListResponse(
        items=[ConnectorLogResponse.model_validate(i) for i in items],
        total=total,
    )


@router.get("/{log_id}", response_model=ConnectorLogResponse)
async def get_log(
    log_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    log_repo = LogRepository(db)
    log = await log_repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log não encontrado")

    # Verify ownership via distributor config
    dist_repo = DistributorRepository(db)
    config = await dist_repo.get_by_id(log.distributor_config_id, user_id)
    if not config:
        raise HTTPException(status_code=404, detail="Log não encontrado")

    return ConnectorLogResponse.model_validate(log)

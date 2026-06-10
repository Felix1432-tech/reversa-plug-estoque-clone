import uuid
import asyncio
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user_id
from app.repositories.distributor_repo import DistributorRepository
from app.repositories.log_repo import LogRepository
from app.schemas.distributor import (
    DistributorCreate,
    DistributorResponse,
    DistributorUpdate,
    RunConnectorResponse,
    TestConnectionResponse,
)
from app.services.connector_runner import ConnectorRunner

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/distributors", tags=["distributors"])


@router.post("", response_model=DistributorResponse, status_code=201)
async def create_distributor(
    body: DistributorCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = DistributorRepository(db)
    existing = await repo.list_by_user(user_id)
    for e in existing:
        if e.distributor_type == body.distributor_type:
            raise HTTPException(status_code=409, detail="Distribuidor já configurado")

    config = await repo.create(
        user_id=user_id,
        distributor_type=body.distributor_type,
        credentials=body.credentials.model_dump(),
        settings=body.settings,
    )
    return config


@router.get("", response_model=list[DistributorResponse])
async def list_distributors(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = DistributorRepository(db)
    return await repo.list_by_user(user_id)


@router.put("/{config_id}", response_model=DistributorResponse)
async def update_distributor(
    config_id: uuid.UUID,
    body: DistributorUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = DistributorRepository(db)
    config = await repo.get_by_id(config_id, user_id)
    if not config:
        raise HTTPException(status_code=404, detail="Distribuidor não encontrado")

    return await repo.update(
        config,
        credentials=body.credentials.model_dump() if body.credentials else None,
        settings=body.settings,
    )


@router.delete("/{config_id}", status_code=204)
async def delete_distributor(
    config_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = DistributorRepository(db)
    config = await repo.get_by_id(config_id, user_id)
    if not config:
        raise HTTPException(status_code=404, detail="Distribuidor não encontrado")
    await repo.delete(config)


@router.post("/{config_id}/test", response_model=TestConnectionResponse)
async def test_connection(
    config_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    runner = ConnectorRunner(db)
    result = await runner.test_connection(config_id, user_id)
    return TestConnectionResponse(**result)


@router.post("/{config_id}/run", response_model=RunConnectorResponse, status_code=202)
async def run_connector(
    config_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = DistributorRepository(db)
    config = await repo.get_by_id(config_id, user_id)
    if not config:
        raise HTTPException(status_code=404, detail="Distribuidor não encontrado")

    log_repo = LogRepository(db)
    running = await log_repo.has_running(config_id)
    if running:
        raise HTTPException(
            status_code=409,
            detail=f"Extração já em andamento: {running.id}",
        )

    # Create log entry synchronously, run extraction in background
    log = await log_repo.create(config_id)

    async def _run():
        from app.db.session import async_session_factory
        async with async_session_factory() as session:
            runner = ConnectorRunner(session)
            await runner.run_extraction(config_id, user_id)

    background_tasks.add_task(asyncio.ensure_future, _run())

    return RunConnectorResponse(log_id=log.id, status="running")

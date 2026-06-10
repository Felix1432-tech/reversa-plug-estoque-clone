import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.connector_log import ConnectorLog


class LogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, distributor_config_id: uuid.UUID) -> ConnectorLog:
        log = ConnectorLog(distributor_config_id=distributor_config_id)
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)
        return log

    async def finish(
        self,
        log: ConnectorLog,
        status: str,
        products_found: int = 0,
        products_created: int = 0,
        products_updated: int = 0,
        errors_count: int = 0,
        error_details: list | None = None,
    ):
        log.finished_at = datetime.now(timezone.utc)
        log.status = status
        log.products_found = products_found
        log.products_created = products_created
        log.products_updated = products_updated
        log.errors_count = errors_count
        log.error_details = error_details or []
        await self.session.commit()

    async def get_by_id(self, log_id: uuid.UUID) -> ConnectorLog | None:
        result = await self.session.execute(
            select(ConnectorLog).where(ConnectorLog.id == log_id)
        )
        return result.scalar_one_or_none()

    async def list_by_distributor(
        self, distributor_config_id: uuid.UUID, limit: int = 30, offset: int = 0
    ) -> tuple[list[ConnectorLog], int]:
        count_q = select(func.count(ConnectorLog.id)).where(
            ConnectorLog.distributor_config_id == distributor_config_id
        )
        total = (await self.session.execute(count_q)).scalar() or 0

        query = (
            select(ConnectorLog)
            .where(ConnectorLog.distributor_config_id == distributor_config_id)
            .order_by(ConnectorLog.started_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = (await self.session.execute(query)).scalars().all()
        return list(items), total

    async def list_by_user_distributors(
        self, distributor_config_ids: list[uuid.UUID], limit: int = 30, offset: int = 0
    ) -> tuple[list[ConnectorLog], int]:
        count_q = select(func.count(ConnectorLog.id)).where(
            ConnectorLog.distributor_config_id.in_(distributor_config_ids)
        )
        total = (await self.session.execute(count_q)).scalar() or 0

        query = (
            select(ConnectorLog)
            .where(ConnectorLog.distributor_config_id.in_(distributor_config_ids))
            .order_by(ConnectorLog.started_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = (await self.session.execute(query)).scalars().all()
        return list(items), total

    async def has_running(self, distributor_config_id: uuid.UUID) -> ConnectorLog | None:
        result = await self.session.execute(
            select(ConnectorLog).where(
                ConnectorLog.distributor_config_id == distributor_config_id,
                ConnectorLog.status == "running",
            )
        )
        return result.scalar_one_or_none()

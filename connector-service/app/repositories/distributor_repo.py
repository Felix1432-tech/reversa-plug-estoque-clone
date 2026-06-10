import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.distributor import DistributorConfig
from app.services.encryption import encryption_service


class DistributorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, user_id: uuid.UUID, distributor_type: str, credentials: dict, settings: dict
    ) -> DistributorConfig:
        encrypted = encryption_service.encrypt(credentials)
        config = DistributorConfig(
            user_id=user_id,
            distributor_type=distributor_type,
            credentials=encrypted,
            status="configured",
            settings=settings,
        )
        self.session.add(config)
        await self.session.commit()
        await self.session.refresh(config)
        return config

    async def get_by_id(self, config_id: uuid.UUID, user_id: uuid.UUID) -> DistributorConfig | None:
        result = await self.session.execute(
            select(DistributorConfig).where(
                DistributorConfig.id == config_id,
                DistributorConfig.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> list[DistributorConfig]:
        result = await self.session.execute(
            select(DistributorConfig)
            .where(DistributorConfig.user_id == user_id)
            .order_by(DistributorConfig.distributor_type)
        )
        return list(result.scalars().all())

    async def update(
        self,
        config: DistributorConfig,
        credentials: dict | None = None,
        settings: dict | None = None,
    ) -> DistributorConfig:
        if credentials is not None:
            config.credentials = encryption_service.encrypt(credentials)
        if settings is not None:
            config.settings = settings
        await self.session.commit()
        await self.session.refresh(config)
        return config

    async def delete(self, config: DistributorConfig):
        await self.session.execute(
            delete(DistributorConfig).where(DistributorConfig.id == config.id)
        )
        await self.session.commit()

    async def update_status(
        self, config: DistributorConfig, status: str, error: str | None = None
    ):
        config.status = status
        config.last_error = error
        await self.session.commit()

    async def update_last_sync(self, config: DistributorConfig, sync_time):
        config.last_sync_at = sync_time
        config.status = "configured"
        config.last_error = None
        await self.session.commit()

    def decrypt_credentials(self, config: DistributorConfig) -> dict:
        return encryption_service.decrypt(config.credentials)

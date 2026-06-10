import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.base import ProductData
from app.models.product import Product


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_products(
        self, distributor_config_id: uuid.UUID, products: list[ProductData]
    ) -> tuple[int, int]:
        """Upsert products. Returns (created_count, updated_count)."""
        if not products:
            return 0, 0

        created = 0
        updated = 0

        for p in products:
            stmt = insert(Product).values(
                distributor_config_id=distributor_config_id,
                sku=p.sku,
                name=p.name,
                description=p.description,
                price=p.price,
                stock_quantity=p.stock_quantity,
                weight=p.weight,
                height=p.height,
                width=p.width,
                length=p.length,
                photos=p.photos,
                fiscal_data=p.fiscal_data,
                raw_data=p.raw_data,
                status="available",
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["distributor_config_id", "sku"],
                set_={
                    "name": stmt.excluded.name,
                    "description": stmt.excluded.description,
                    "price": stmt.excluded.price,
                    "stock_quantity": stmt.excluded.stock_quantity,
                    "weight": stmt.excluded.weight,
                    "height": stmt.excluded.height,
                    "width": stmt.excluded.width,
                    "length": stmt.excluded.length,
                    "photos": stmt.excluded.photos,
                    "fiscal_data": stmt.excluded.fiscal_data,
                    "raw_data": stmt.excluded.raw_data,
                    "status": "available",
                    "updated_at": func.now(),
                },
            )
            result = await self.session.execute(stmt)
            # xmax = 0 means INSERT, otherwise UPDATE
            # For simplicity, count by checking if row existed
            if result.rowcount:
                # Check if it was an insert or update by querying
                existing = await self.session.execute(
                    select(Product.created_at, Product.updated_at).where(
                        Product.distributor_config_id == distributor_config_id,
                        Product.sku == p.sku,
                    )
                )
                row = existing.one()
                if row.created_at == row.updated_at:
                    created += 1
                else:
                    updated += 1

        await self.session.commit()
        return created, updated

    async def mark_absent_unavailable(
        self, distributor_config_id: uuid.UUID, found_skus: list[str]
    ) -> int:
        """Mark products not in found_skus as unavailable. Returns count of affected rows."""
        stmt = (
            update(Product)
            .where(
                Product.distributor_config_id == distributor_config_id,
                Product.sku.notin_(found_skus),
                Product.status == "available",
            )
            .values(status="unavailable", updated_at=datetime.now(timezone.utc))
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def list_products(
        self,
        user_distributor_ids: list[uuid.UUID],
        distributor_type: str | None = None,
        status: str | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Product], int]:
        """List products with filters. Returns (items, total_count)."""
        query = select(Product).where(
            Product.distributor_config_id.in_(user_distributor_ids)
        )
        count_query = select(func.count(Product.id)).where(
            Product.distributor_config_id.in_(user_distributor_ids)
        )

        if status:
            query = query.where(Product.status == status)
            count_query = count_query.where(Product.status == status)
        if search:
            query = query.where(Product.name.ilike(f"%{search}%"))
            count_query = count_query.where(Product.name.ilike(f"%{search}%"))

        total = (await self.session.execute(count_query)).scalar() or 0
        items = (
            await self.session.execute(
                query.order_by(Product.updated_at.desc()).limit(limit).offset(offset)
            )
        ).scalars().all()

        return list(items), total

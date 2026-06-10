import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.base import ProductData
from app.connectors.registry import get_connector
from app.repositories.distributor_repo import DistributorRepository
from app.repositories.log_repo import LogRepository
from app.repositories.product_repo import ProductRepository
from app.services.photo_storage import photo_storage

logger = logging.getLogger(__name__)


class ConnectorRunner:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.dist_repo = DistributorRepository(session)
        self.product_repo = ProductRepository(session)
        self.log_repo = LogRepository(session)

    async def test_connection(self, config_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        config = await self.dist_repo.get_by_id(config_id, user_id)
        if not config:
            return {"status": "error", "message": "Distribuidor não encontrado"}

        credentials = self.dist_repo.decrypt_credentials(config)
        connector = get_connector(config.distributor_type, credentials, config.settings)

        try:
            await connector.authenticate()
            return {"status": "success", "message": f"Login bem-sucedido no {config.distributor_type.upper()}"}
        except Exception as exc:
            return {"status": "error", "message": f"Login falhou: {exc}"}
        finally:
            await connector.close()

    async def run_extraction(self, config_id: uuid.UUID, user_id: uuid.UUID) -> uuid.UUID:
        config = await self.dist_repo.get_by_id(config_id, user_id)
        if not config:
            raise ValueError("Distribuidor não encontrado")

        # Check for running extraction
        running = await self.log_repo.has_running(config_id)
        if running:
            raise ValueError(f"Extração já em andamento: {running.id}")

        log = await self.log_repo.create(config_id)
        credentials = self.dist_repo.decrypt_credentials(config)
        connector = get_connector(config.distributor_type, credentials, config.settings)

        errors = []
        try:
            await connector.authenticate()
            products: list[ProductData] = await connector.fetch_catalog()

            # Upload photos to B2
            for product in products:
                uploaded_urls = []
                for i, photo_url in enumerate(product.photos):
                    try:
                        import httpx
                        async with httpx.AsyncClient(timeout=15) as client:
                            resp = await client.get(photo_url)
                            if resp.status_code == 200:
                                filename = f"photo_{i}.jpg"
                                url = await photo_storage.upload_photo(
                                    str(user_id),
                                    config.distributor_type,
                                    product.sku,
                                    filename,
                                    resp.content,
                                    content_type=resp.headers.get("content-type", "image/jpeg"),
                                )
                                uploaded_urls.append(url)
                            else:
                                uploaded_urls.append(photo_url)
                    except Exception as exc:
                        logger.warning("Failed to upload photo for %s: %s", product.sku, exc)
                        uploaded_urls.append(photo_url)
                        errors.append({"sku": product.sku, "error": f"Photo upload failed: {exc}"})
                product.photos = uploaded_urls

            # Upsert products
            created, updated = await self.product_repo.upsert_products(config_id, products)

            # Mark absent products as unavailable
            found_skus = [p.sku for p in products]
            absent_count = await self.product_repo.mark_absent_unavailable(config_id, found_skus)

            # Update distributor status
            await self.dist_repo.update_last_sync(config, datetime.now(timezone.utc))

            # Finish log
            status = "success" if not errors else "partial"
            await self.log_repo.finish(
                log,
                status=status,
                products_found=len(products),
                products_created=created,
                products_updated=updated,
                errors_count=len(errors),
                error_details=errors,
            )

            logger.info(
                "Extraction complete for %s: %d found, %d created, %d updated, %d absent marked, %d errors",
                config.distributor_type, len(products), created, updated, absent_count, len(errors),
            )

        except Exception as exc:
            logger.error("Extraction failed for %s: %s", config.distributor_type, exc)
            await self.dist_repo.update_status(config, "error", str(exc))
            await self.log_repo.finish(
                log,
                status="error",
                errors_count=1,
                error_details=[{"error": str(exc)}],
            )
        finally:
            await connector.close()

        return log.id

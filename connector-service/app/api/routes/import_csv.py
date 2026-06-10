import json
import uuid
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user_id
from app.connectors.csv_import import CSVImportConnector
from app.repositories.distributor_repo import DistributorRepository
from app.repositories.log_repo import LogRepository
from app.repositories.product_repo import ProductRepository
from app.schemas.distributor import RunConnectorResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/import", tags=["import"])


@router.post("/csv", response_model=RunConnectorResponse, status_code=202)
async def import_csv(
    file: UploadFile = File(...),
    distributor_config_id: str = Form(...),
    column_mapping: str = Form("{}"),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    config_id = uuid.UUID(distributor_config_id)
    dist_repo = DistributorRepository(db)
    config = await dist_repo.get_by_id(config_id, user_id)
    if not config:
        raise HTTPException(status_code=404, detail="Distribuidor não encontrado")

    try:
        mapping = json.loads(column_mapping)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="column_mapping deve ser JSON válido")

    data = await file.read()
    filename = file.filename or "upload.csv"

    connector = CSVImportConnector(credentials={})
    connector.set_file(data, filename, mapping)

    log_repo = LogRepository(db)
    log = await log_repo.create(config_id)

    try:
        products = await connector.fetch_catalog()
        product_repo = ProductRepository(db)
        created, updated = await product_repo.upsert_products(config_id, products)

        await log_repo.finish(
            log,
            status="success",
            products_found=len(products),
            products_created=created,
            products_updated=updated,
        )
        logger.info("CSV import: %d products (%d new, %d updated)", len(products), created, updated)
    except Exception as exc:
        await log_repo.finish(log, status="error", errors_count=1, error_details=[{"error": str(exc)}])
        raise HTTPException(status_code=422, detail=str(exc))

    return RunConnectorResponse(log_id=log.id, status="success")

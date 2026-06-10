import logging
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

class CredentialFilter(logging.Filter):
    """Prevent credentials from appearing in logs."""
    SENSITIVE = ("password", "senha", "secret", "token", "credentials", "encryption_key")

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage().lower()
        for word in self.SENSITIVE:
            if word in msg:
                record.msg = "[REDACTED — sensitive content]"
                record.args = None
                break
        return True


# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logging.getLogger().addFilter(CredentialFilter())

# Suppress noisy loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("playwright").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting connector-service")
    # Import connectors to trigger registration
    import app.connectors.dpk  # noqa: F401
    import app.connectors.furacao  # noqa: F401
    import app.connectors.pellegrino  # noqa: F401
    import app.connectors.laquila_drive  # noqa: F401
    import app.connectors.rufato  # noqa: F401
    import app.connectors.rolemarmaster  # noqa: F401
    import app.connectors.csv_import  # noqa: F401

    # Start scheduler
    from app.services.scheduler import start_scheduler, stop_scheduler
    start_scheduler()

    yield

    stop_scheduler()
    logger.info("Shutting down connector-service")


app = FastAPI(
    title="Connector Service",
    description="Serviço de conectores de distribuidores — extração de catálogo via RPA e Google Drive",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api.routes.distributors import router as distributors_router
from app.api.routes.logs import router as logs_router
from app.api.routes.products import router as products_router
from app.api.routes.import_csv import router as import_router
from app.api.routes.health import router as health_router

app.include_router(distributors_router, prefix="/api/v1")
app.include_router(logs_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(import_router, prefix="/api/v1")
app.include_router(health_router)

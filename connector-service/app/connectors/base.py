import asyncio
import functools
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

DISTRIBUTOR_TYPES = (
    "dpk", "furacao", "rufato", "isapa", "pellegrino", "laquila", "rolemarmaster"
)


@dataclass
class ProductData:
    sku: str
    name: str
    description: str | None = None
    price: float | None = None
    stock_quantity: int | None = None
    weight: float | None = None
    height: float | None = None
    width: float | None = None
    length: float | None = None
    photos: list[str] = field(default_factory=list)
    fiscal_data: dict = field(default_factory=dict)
    raw_data: dict = field(default_factory=dict)


def retry(max_attempts: int = 3, backoff: list[int] | None = None):
    if backoff is None:
        backoff = [5, 15, 45]

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc
                    if attempt < max_attempts - 1:
                        delay = backoff[min(attempt, len(backoff) - 1)]
                        logger.warning(
                            "Attempt %d/%d failed for %s: %s. Retrying in %ds...",
                            attempt + 1, max_attempts, func.__name__, exc, delay,
                        )
                        await asyncio.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


class BaseConnector(ABC):
    def __init__(self, credentials: dict, settings: dict | None = None):
        self.credentials = credentials
        self.settings = settings or {}

    @abstractmethod
    async def authenticate(self) -> bool:
        """Login to distributor. Returns True on success, raises on failure."""

    @abstractmethod
    async def fetch_catalog(self) -> list[ProductData]:
        """Extract full catalog. Returns list of normalized products."""

    @abstractmethod
    async def fetch_stock(self) -> dict[str, int | None]:
        """Fetch current stock levels. Returns {sku: quantity}."""

    @abstractmethod
    async def health_check(self) -> dict:
        """Quick check if connector can reach the distributor. Returns status dict."""

    async def close(self):
        """Cleanup resources. Override if connector needs cleanup (e.g. browser)."""

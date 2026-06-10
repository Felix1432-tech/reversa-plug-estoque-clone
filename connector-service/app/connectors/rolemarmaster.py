import logging

from app.connectors.rufato import RPAConnectorBase
from app.connectors.registry import register_connector

logger = logging.getLogger(__name__)


@register_connector("rolemarmaster")
class RolemarmasterConnector(RPAConnectorBase):
    """Rolemarmaster connector — catalog only, no stock available."""
    BASE_URL = "https://rolemarmaster.com"
    LOGIN_PATH = "/login"
    CATALOG_PATH = "/produtos"
    HAS_STOCK = False

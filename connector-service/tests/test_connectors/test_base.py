import pytest
from app.connectors.base import BaseConnector, ProductData, retry


def test_base_connector_cannot_be_instantiated():
    """BaseConnector is abstract — direct instantiation should raise."""
    with pytest.raises(TypeError):
        BaseConnector(credentials={})


def test_subclass_without_methods_raises():
    """A subclass that doesn't implement abstract methods should raise."""
    class BadConnector(BaseConnector):
        pass

    with pytest.raises(TypeError):
        BadConnector(credentials={})


def test_subclass_with_all_methods():
    """A subclass implementing all methods should instantiate fine."""
    class GoodConnector(BaseConnector):
        async def authenticate(self):
            return True

        async def fetch_catalog(self):
            return []

        async def fetch_stock(self):
            return {}

        async def health_check(self):
            return {"status": "ok"}

    connector = GoodConnector(credentials={"login": "x", "password": "y"})
    assert connector.credentials == {"login": "x", "password": "y"}
    assert connector.settings == {}


def test_product_data_defaults():
    """ProductData should have sensible defaults."""
    p = ProductData(sku="ABC-123", name="Test Product")
    assert p.sku == "ABC-123"
    assert p.name == "Test Product"
    assert p.description is None
    assert p.price is None
    assert p.stock_quantity is None
    assert p.photos == []
    assert p.fiscal_data == {}
    assert p.raw_data == {}


@pytest.mark.asyncio
async def test_retry_decorator_succeeds_on_second_attempt():
    call_count = 0

    @retry(max_attempts=3, backoff=[0, 0, 0])
    async def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ConnectionError("Temporary failure")
        return "ok"

    result = await flaky()
    assert result == "ok"
    assert call_count == 2


@pytest.mark.asyncio
async def test_retry_decorator_exhausts_attempts():
    @retry(max_attempts=2, backoff=[0, 0])
    async def always_fails():
        raise ConnectionError("Permanent failure")

    with pytest.raises(ConnectionError, match="Permanent failure"):
        await always_fails()

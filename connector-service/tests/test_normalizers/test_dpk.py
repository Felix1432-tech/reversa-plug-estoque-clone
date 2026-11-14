"""Synthetic WK58-shaped data; NOT a captured or verified DPK response."""
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.normalizers.dpk import normalize_dpk_product


def sample(warehouses):
    return {
        "sku": "WK58", "manufacturer": None, "description": None,
        "purchase_price": "168,90", "warehouses": warehouses,
        "vehicle_applications": [{"model": "SYNTHETIC TEST ONLY"}],
    }


def test_campinas_by_name_not_position():
    result = normalize_dpk_product(
        sample([{"name": "CD São Paulo", "quantity": 99},
                {"name": "CD Campinas", "quantity": 3}]),
        verified_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert result.campinas.quantity == 3
    assert result.campinas.status == "available"
    assert result.purchase_price == Decimal("168.90")
    assert len(result.vehicle_applications) == 1


@pytest.mark.parametrize("quantity", [0, "Indisponível", "sem estoque"])
def test_zero_stock(quantity):
    assert normalize_dpk_product(sample([{"name": "Campinas", "quantity": quantity}])).campinas.status == "zero"


def test_unknown_is_not_zero():
    for warehouses in ([], [{"name": "Campinas", "quantity": None}]):
        item = normalize_dpk_product(sample(warehouses))
        assert item.campinas.quantity is None
        assert item.campinas.status == "unverified"
        assert item.campinas.verified_at is None


def test_ambiguous_campinas_rejected():
    with pytest.raises(ValueError, match="Ambiguous"):
        normalize_dpk_product(sample([{"name": "Campinas", "quantity": 1},
                                      {"name": "CD Campinas", "quantity": 2}]))


def test_invalid_stock_rejected():
    with pytest.raises(ValueError):
        normalize_dpk_product(sample([{"name": "Campinas", "quantity": -1}]))


def test_missing_sku_rejected():
    with pytest.raises(ValueError, match="SKU"):
        normalize_dpk_product({"warehouses": []})

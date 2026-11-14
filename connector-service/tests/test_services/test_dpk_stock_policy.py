"""DPK Campinas inventory policy: synthetic fixtures, no network or marketplace writes."""
from datetime import datetime, timedelta, timezone

import pytest

from app.normalizers.dpk import WarehouseAvailability
from app.services.dpk_stock_policy import evaluate_campinas_stock


NOW = datetime(2026, 11, 14, 19, 0, tzinfo=timezone.utc)


def stock(quantity, *, verified_at=NOW, warehouse="CD Campinas"):
    status = "unverified" if quantity is None else ("zero" if quantity == 0 else "available")
    return WarehouseAvailability(warehouse, quantity, status, verified_at)


@pytest.mark.parametrize("quantity,expected", [(886, "keep_active"), (6, "keep_active"),
                                                (5, "pause"), (1, "pause"), (0, "pause")])
def test_minimum_five(quantity, expected):
    assert evaluate_campinas_stock(stock(quantity), now=NOW).action == expected


def test_unknown_stock_pauses():
    assert evaluate_campinas_stock(stock(None), now=NOW).reason == "unknown_stock"


def test_stale_stock_pauses():
    old = NOW - timedelta(minutes=31)
    assert evaluate_campinas_stock(stock(886, verified_at=old), now=NOW).action == "pause"


def test_missing_timestamp_pauses():
    assert evaluate_campinas_stock(stock(886, verified_at=None), now=NOW).action == "pause"


def test_other_depot_not_used():
    assert evaluate_campinas_stock(stock(900, warehouse="BH"), now=NOW).reason == "wrong_warehouse"


def test_no_automatic_reactivation():
    decision = evaluate_campinas_stock(stock(886), now=NOW, currently_paused=True)
    assert decision.action == "review"


def test_future_timestamp_pauses():
    future = NOW + timedelta(seconds=10)
    assert evaluate_campinas_stock(stock(886, verified_at=future), now=NOW).action == "pause"


def test_naive_now_rejected():
    with pytest.raises(ValueError):
        evaluate_campinas_stock(stock(886), now=datetime(2026, 11, 14))

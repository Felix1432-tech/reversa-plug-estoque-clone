"""Fail-safe DPK Campinas inventory decision policy.

Pure decision logic only. No marketplace API calls or automatic reactivation.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.normalizers.dpk import WarehouseAvailability

DEFAULT_MINIMUM_STOCK = 5
DEFAULT_MAX_AGE = timedelta(minutes=30)


@dataclass(frozen=True)
class StockDecision:
    action: str  # keep_active, pause, review
    reason: str
    quantity: int | None


def evaluate_campinas_stock(
    availability: WarehouseAvailability,
    *,
    now: datetime,
    minimum_stock: int = DEFAULT_MINIMUM_STOCK,
    max_age: timedelta = DEFAULT_MAX_AGE,
    currently_paused: bool = False,
) -> StockDecision:
    """Decide desired state. A paused listing is NEVER auto-reactivated.

    'keep_active' means no pause is needed, not permission to publish or resume.
    """
    if minimum_stock < 0 or max_age <= timedelta(0):
        raise ValueError("Invalid stock policy configuration")
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    if availability.warehouse != "CD Campinas":
        return StockDecision("pause", "wrong_warehouse", availability.quantity)
    if availability.quantity is None or availability.status == "unverified":
        return StockDecision("pause", "unknown_stock", availability.quantity)
    if availability.quantity < 0:
        return StockDecision("pause", "invalid_stock", availability.quantity)
    if availability.verified_at is None or availability.verified_at.tzinfo is None:
        return StockDecision("pause", "missing_verification", availability.quantity)
    age = now - availability.verified_at
    if age < timedelta(0) or age > max_age:
        return StockDecision("pause", "stale_or_future_verification", availability.quantity)
    if availability.quantity <= minimum_stock:
        return StockDecision("pause", "minimum_stock_reached", availability.quantity)
    if currently_paused:
        return StockDecision("review", "manual_reactivation_required", availability.quantity)
    return StockDecision("keep_active", "stock_above_minimum", availability.quantity)

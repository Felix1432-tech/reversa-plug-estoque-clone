"""Pure DPK payload normalizer. No network, credentials, or side effects."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re
import unicodedata


@dataclass(frozen=True)
class WarehouseAvailability:
    warehouse: str
    quantity: int | None
    status: str  # available, zero, unverified
    verified_at: datetime | None


@dataclass(frozen=True)
class NormalizedDPKProduct:
    sku: str
    manufacturer: str | None
    description: str | None
    purchase_price: Decimal | None
    campinas: WarehouseAvailability
    vehicle_applications: tuple[dict, ...]


def _fold(value: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", value)
                   if not unicodedata.combining(c)).casefold().strip()


def _quantity(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError("Boolean is not a stock quantity")
    if isinstance(value, int):
        if value < 0:
            raise ValueError("Negative stock quantity")
        return value
    if isinstance(value, str):
        cleaned = value.strip()
        if _fold(cleaned) in {"indisponivel", "sem estoque"}:
            return 0
        if re.fullmatch(r"\d+", cleaned):
            return int(cleaned)
    raise ValueError("Unrecognized stock quantity")


def _money(value: object) -> Decimal | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ValueError("Invalid price")
    raw = str(value).strip().replace("R$", "").strip()
    if "," in raw:
        raw = raw.replace(".", "").replace(",", ".")
    try:
        amount = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError("Invalid price") from exc
    if not amount.is_finite() or amount < 0:
        raise ValueError("Invalid price")
    return amount


def normalize_dpk_product(payload: dict, *, verified_at: datetime | None = None) -> NormalizedDPKProduct:
    """Normalize a sanitized adapter payload; unknown stock is not zero."""
    sku = str(payload.get("sku") or "").strip()
    if not sku:
        raise ValueError("SKU is required")
    warehouses = payload.get("warehouses") or []
    if not isinstance(warehouses, list):
        raise ValueError("warehouses must be a list")
    matches = [w for w in warehouses if isinstance(w, dict)
               and _fold(str(w.get("name") or "")) in {"campinas", "cd campinas"}]
    if len(matches) > 1:
        raise ValueError("Ambiguous Campinas warehouses")
    quantity = _quantity(matches[0].get("quantity")) if matches else None
    status = "unverified" if quantity is None else ("zero" if quantity == 0 else "available")
    apps = payload.get("vehicle_applications") or []
    if not isinstance(apps, list) or not all(isinstance(a, dict) for a in apps):
        raise ValueError("Invalid vehicle applications")
    return NormalizedDPKProduct(
        sku=sku,
        manufacturer=payload.get("manufacturer"),
        description=payload.get("description"),
        purchase_price=_money(payload.get("purchase_price")),
        campinas=WarehouseAvailability(
            warehouse="CD Campinas",
            quantity=quantity,
            status=status,
            verified_at=verified_at if quantity is not None else None,
        ),
        vehicle_applications=tuple(apps),
    )

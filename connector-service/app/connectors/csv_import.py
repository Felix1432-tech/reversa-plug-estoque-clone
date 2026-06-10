import csv
import io
import logging

import openpyxl

from app.connectors.base import BaseConnector, ProductData
from app.connectors.registry import register_connector

logger = logging.getLogger(__name__)


@register_connector("csv_import")
class CSVImportConnector(BaseConnector):
    """Manual CSV/Excel import as fallback. Not a real connector — processes uploaded files."""

    def __init__(self, credentials: dict, settings: dict | None = None):
        super().__init__(credentials, settings)
        self._file_data: bytes | None = None
        self._filename: str = ""
        self._column_mapping: dict = {}

    def set_file(self, data: bytes, filename: str, column_mapping: dict):
        self._file_data = data
        self._filename = filename
        self._column_mapping = column_mapping

    async def authenticate(self) -> bool:
        return True

    async def fetch_catalog(self) -> list[ProductData]:
        if not self._file_data:
            raise ValueError("No file set. Call set_file() first.")

        if self._filename.endswith((".xlsx", ".xls")):
            rows = self._parse_excel(self._file_data)
        elif self._filename.endswith(".csv"):
            rows = self._parse_csv(self._file_data)
        else:
            raise ValueError(f"Unsupported file format: {self._filename}")

        mapping = self._column_mapping
        products = []

        for row in rows:
            sku = row.get(mapping.get("sku", "sku"))
            name = row.get(mapping.get("name", "name"))
            if not sku or not name:
                continue

            price_val = row.get(mapping.get("price", "price"))
            stock_val = row.get(mapping.get("stock", "stock"))

            products.append(ProductData(
                sku=str(sku).strip(),
                name=str(name).strip(),
                description=str(row.get(mapping.get("description", "description"), "") or ""),
                price=self._to_float(price_val),
                stock_quantity=self._to_int(stock_val),
                weight=self._to_float(row.get(mapping.get("weight", "weight"))),
                photos=[],
                raw_data=row,
            ))

        logger.info("CSV import: parsed %d products from %s", len(products), self._filename)
        return products

    async def fetch_stock(self) -> dict[str, int | None]:
        catalog = await self.fetch_catalog()
        return {p.sku: p.stock_quantity for p in catalog}

    async def health_check(self) -> dict:
        return {"status": "ok", "type": "csv_import"}

    def _parse_excel(self, data: bytes) -> list[dict]:
        wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return []
        headers = [str(h).strip().lower() if h else f"col_{i}" for i, h in enumerate(rows[0])]
        return [dict(zip(headers, row)) for row in rows[1:] if any(row)]

    def _parse_csv(self, data: bytes) -> list[dict]:
        text = data.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        return [{k.strip().lower(): v for k, v in row.items()} for row in reader]

    @staticmethod
    def _to_float(val) -> float | None:
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return float(val)
        import re
        clean = re.sub(r"[^\d,.]", "", str(val))
        clean = clean.replace(".", "").replace(",", ".")
        try:
            return float(clean)
        except ValueError:
            return None

    @staticmethod
    def _to_int(val) -> int | None:
        if val is None:
            return None
        if isinstance(val, int):
            return val
        import re
        digits = re.sub(r"\D", "", str(val))
        return int(digits) if digits else None

import json
import logging
import os
import tempfile

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO

from app.connectors.base import BaseConnector, ProductData, retry
from app.connectors.registry import register_connector

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
DEFAULT_FOLDER_ID = "1fTGWuCD_gB8xj8dveddGE-2XDZOoh1jW"


@register_connector("laquila")
class LAquilaDriveConnector(BaseConnector):
    """L'Aquila connector via Google Drive API — reads photos, prices, description, fiscal data."""

    def __init__(self, credentials: dict, settings: dict | None = None):
        super().__init__(credentials, settings)
        self._service = None
        self._folder_id = (settings or {}).get("drive_folder_id", DEFAULT_FOLDER_ID)

    def _build_service(self):
        sa_json = self.credentials.get("service_account_json", "")
        if isinstance(sa_json, str):
            sa_info = json.loads(sa_json)
        else:
            sa_info = sa_json
        creds = Credentials.from_service_account_info(sa_info, scopes=SCOPES)
        self._service = build("drive", "v3", credentials=creds)

    @retry(max_attempts=3, backoff=[5, 15, 45])
    async def authenticate(self) -> bool:
        self._build_service()
        # Verify access to the folder
        result = self._service.files().list(
            q=f"'{self._folder_id}' in parents and trashed=false",
            pageSize=1,
            fields="files(id, name)",
        ).execute()
        logger.info("L'Aquila Drive auth OK, folder accessible")
        return True

    @retry(max_attempts=3, backoff=[5, 15, 45])
    async def fetch_catalog(self) -> list[ProductData]:
        if not self._service:
            self._build_service()

        products = []

        # List all files in the folder
        files = self._list_folder_recursive(self._folder_id)
        spreadsheets = [f for f in files if f["mimeType"] in (
            "application/vnd.google-apps.spreadsheet",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/csv",
        )]
        image_files = [f for f in files if f["mimeType"].startswith("image/")]

        # Build photo map: folder_name -> [photo_urls]
        photo_map = {}
        for img in image_files:
            parent = img.get("parent_name", "unknown")
            photo_map.setdefault(parent, []).append(img)

        # Parse spreadsheet for product data
        for sheet in spreadsheets:
            try:
                rows = self._read_spreadsheet(sheet)
                for row in rows:
                    sku = row.get("sku") or row.get("codigo") or row.get("SKU") or row.get("Código")
                    name = row.get("nome") or row.get("name") or row.get("Nome") or row.get("produto")
                    if not sku or not name:
                        continue

                    # Match photos by SKU folder
                    sku_photos = photo_map.get(sku, [])
                    photo_urls = [
                        f"https://drive.google.com/uc?id={p['id']}&export=download"
                        for p in sku_photos
                    ]

                    price_val = row.get("preco") or row.get("preço") or row.get("Preço") or row.get("price")
                    fiscal = {}
                    for key in ("ncm", "NCM", "gtin", "GTIN", "ean", "EAN"):
                        if key in row and row[key]:
                            fiscal[key.lower()] = str(row[key])

                    products.append(ProductData(
                        sku=str(sku),
                        name=str(name),
                        description=str(row.get("descricao") or row.get("descrição") or row.get("Descrição") or ""),
                        price=self._parse_number(price_val),
                        stock_quantity=None,
                        photos=photo_urls,
                        fiscal_data=fiscal,
                        raw_data=row,
                    ))
            except Exception as exc:
                logger.warning("L'Aquila: failed to parse spreadsheet %s: %s", sheet["name"], exc)

        logger.info("L'Aquila Drive: extracted %d products", len(products))
        return products

    def _list_folder_recursive(self, folder_id: str, parent_name: str = "") -> list[dict]:
        results = []
        page_token = None
        while True:
            response = self._service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                pageSize=1000,
                fields="nextPageToken, files(id, name, mimeType, parents)",
                pageToken=page_token,
            ).execute()

            for f in response.get("files", []):
                f["parent_name"] = parent_name
                if f["mimeType"] == "application/vnd.google-apps.folder":
                    results.extend(self._list_folder_recursive(f["id"], f["name"]))
                else:
                    results.append(f)

            page_token = response.get("nextPageToken")
            if not page_token:
                break
        return results

    def _read_spreadsheet(self, file_info: dict) -> list[dict]:
        """Download and parse spreadsheet."""
        if file_info["mimeType"] == "application/vnd.google-apps.spreadsheet":
            # Export as xlsx
            request = self._service.files().export_media(
                fileId=file_info["id"],
                mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            request = self._service.files().get_media(fileId=file_info["id"])

        buffer = BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        buffer.seek(0)

        import openpyxl
        wb = openpyxl.load_workbook(buffer, read_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return []

        headers = [str(h).strip().lower() if h else f"col_{i}" for i, h in enumerate(rows[0])]
        return [dict(zip(headers, row)) for row in rows[1:] if any(row)]

    async def fetch_stock(self) -> dict[str, int | None]:
        return {}

    async def health_check(self) -> dict:
        try:
            self._build_service()
            self._service.files().list(
                q=f"'{self._folder_id}' in parents and trashed=false",
                pageSize=1,
                fields="files(id)",
            ).execute()
            return {"status": "ok", "folder_id": self._folder_id}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    async def close(self):
        self._service = None

    @staticmethod
    def _parse_number(val) -> float | None:
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

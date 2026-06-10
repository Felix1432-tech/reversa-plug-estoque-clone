import asyncio
import logging
import random

from playwright.async_api import async_playwright, Browser, Page

from app.connectors.base import BaseConnector, ProductData, retry
from app.connectors.registry import register_connector

logger = logging.getLogger(__name__)

# Selectors will be refined during implementation once site structure is mapped
SELECTORS = {
    "login": {
        "username": 'input[name="email"], input[type="email"], #email',
        "password": 'input[name="password"], input[type="password"], #password',
        "submit": 'button[type="submit"]',
    },
    "catalog": {
        "product_list": ".product-item, .produto, tr.item",
        "product_link": "a[href*='product'], a[href*='detalhe']",
        "next_page": ".pagination .next",
    },
    "product_detail": {
        "sku": ".sku, .codigo",
        "name": "h1, .product-name",
        "description": ".description, .descricao",
        "price": ".price, .preco",
        "stock": ".stock, .estoque",
        "weight": ".weight, .peso",
        "dimensions": ".dimensions, .medidas",
        "photos": ".gallery img, .product-images img",
    },
}


class RPAConnectorBase(BaseConnector):
    """Shared RPA logic for RUFATO, ISAPA, and Rolemarmaster."""

    BASE_URL: str = ""
    LOGIN_PATH: str = "/login"
    CATALOG_PATH: str = "/produtos"
    HAS_STOCK: bool = True

    def __init__(self, credentials: dict, settings: dict | None = None):
        super().__init__(credentials, settings)
        self._browser: Browser | None = None
        self._page: Page | None = None
        self._playwright = None

    async def _init_browser(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = await self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        )
        self._page = await context.new_page()

    async def _human_delay(self, min_s: float = 1.0, max_s: float = 3.0):
        await asyncio.sleep(random.uniform(min_s, max_s))

    @retry(max_attempts=3, backoff=[5, 15, 45])
    async def authenticate(self) -> bool:
        if not self._page:
            await self._init_browser()
        await self._page.goto(
            f"{self.BASE_URL}{self.LOGIN_PATH}", wait_until="networkidle", timeout=30000
        )
        await self._human_delay(0.5, 1.5)

        await self._page.locator(SELECTORS["login"]["username"]).first.fill(self.credentials["login"])
        await self._human_delay(0.3, 0.8)
        await self._page.locator(SELECTORS["login"]["password"]).first.fill(self.credentials["password"])
        await self._human_delay(0.3, 0.8)
        await self._page.locator(SELECTORS["login"]["submit"]).first.click()
        await self._page.wait_for_load_state("networkidle", timeout=15000)

        if "login" in self._page.url.lower():
            raise ConnectionError(f"Login failed at {self.BASE_URL}")

        logger.info("%s login successful", self.__class__.__name__)
        return True

    @retry(max_attempts=3, backoff=[5, 15, 45])
    async def fetch_catalog(self) -> list[ProductData]:
        if not self._page:
            raise RuntimeError("Not authenticated")

        products = []
        await self._page.goto(
            f"{self.BASE_URL}{self.CATALOG_PATH}", wait_until="networkidle", timeout=30000
        )
        await self._human_delay()

        page_num = 1
        while True:
            logger.info("%s: scraping page %d", self.__class__.__name__, page_num)
            try:
                await self._page.wait_for_selector(SELECTORS["catalog"]["product_list"], timeout=10000)
            except Exception:
                break

            links = []
            for el in await self._page.locator(SELECTORS["catalog"]["product_link"]).all():
                href = await el.get_attribute("href")
                if href:
                    links.append(href)

            for href in links:
                try:
                    url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                    await self._page.goto(url, wait_until="networkidle", timeout=30000)
                    await self._human_delay(0.5, 1.0)

                    product = await self._extract_detail()
                    if product:
                        products.append(product)
                except Exception as exc:
                    logger.warning("%s: failed %s: %s", self.__class__.__name__, href, exc)

            # Navigate back to catalog for next page
            await self._page.goto(
                f"{self.BASE_URL}{self.CATALOG_PATH}", wait_until="networkidle", timeout=30000
            )
            next_btn = self._page.locator(SELECTORS["catalog"]["next_page"]).first
            if await next_btn.count() and await next_btn.is_enabled():
                await next_btn.click()
                await self._page.wait_for_load_state("networkidle", timeout=15000)
                await self._human_delay()
                page_num += 1
            else:
                break

        logger.info("%s: extracted %d products", self.__class__.__name__, len(products))
        return products

    async def _extract_detail(self) -> ProductData | None:
        async def safe_text(sel: str) -> str | None:
            el = self._page.locator(sel).first
            if await el.count():
                return (await el.text_content() or "").strip()
            return None

        sku = await safe_text(SELECTORS["product_detail"]["sku"])
        name = await safe_text(SELECTORS["product_detail"]["name"])
        if not sku or not name:
            return None

        from app.connectors.dpk import DPKConnector

        price_text = await safe_text(SELECTORS["product_detail"]["price"])
        stock_text = await safe_text(SELECTORS["product_detail"]["stock"]) if self.HAS_STOCK else None
        weight_text = await safe_text(SELECTORS["product_detail"]["weight"])
        dims_text = await safe_text(SELECTORS["product_detail"]["dimensions"])

        photos = []
        for img in await self._page.locator(SELECTORS["product_detail"]["photos"]).all():
            src = await img.get_attribute("src")
            if src:
                photos.append(src if src.startswith("http") else f"{self.BASE_URL}{src}")

        h, w, l = DPKConnector._parse_dimensions(dims_text) if dims_text else (None, None, None)

        return ProductData(
            sku=sku,
            name=name,
            description=await safe_text(SELECTORS["product_detail"]["description"]),
            price=DPKConnector._parse_price(price_text) if price_text else None,
            stock_quantity=DPKConnector._parse_int(stock_text) if stock_text else None,
            weight=DPKConnector._parse_float(weight_text) if weight_text else None,
            height=h, width=w, length=l,
            photos=photos,
            raw_data={"source_url": self._page.url},
        )

    async def fetch_stock(self) -> dict[str, int | None]:
        catalog = await self.fetch_catalog()
        return {p.sku: p.stock_quantity for p in catalog}

    async def health_check(self) -> dict:
        try:
            if not self._page:
                await self._init_browser()
            await self._page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=15000)
            return {"status": "ok", "url": self.BASE_URL}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    async def close(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._browser = self._page = self._playwright = None


@register_connector("rufato")
class RUFATOConnector(RPAConnectorBase):
    BASE_URL = "https://www.rufato.com.br"  # URL to be confirmed
    LOGIN_PATH = "/login"
    CATALOG_PATH = "/produtos"
    HAS_STOCK = True


@register_connector("isapa")
class ISAPAConnector(RPAConnectorBase):
    BASE_URL = "https://www.isapa.com.br"  # URL to be confirmed
    LOGIN_PATH = "/login"
    CATALOG_PATH = "/produtos"
    HAS_STOCK = True

import asyncio
import logging
import random

from playwright.async_api import async_playwright, Browser, Page

from app.connectors.base import BaseConnector, ProductData, retry
from app.connectors.registry import register_connector

logger = logging.getLogger(__name__)

BASE_URL = "https://compreonline.pellegrino.com.br"

SELECTORS = {
    "login": {
        "username": 'input[name="email"], input[type="email"], #email',
        "password": 'input[name="password"], input[type="password"], #password',
        "submit": 'button[type="submit"], .btn-login',
    },
    "catalog": {
        "product_list": ".product-item, .product-card, .produto",
        "product_link": "a[href*='product'], a[href*='produto']",
        "next_page": ".pagination .next, a[rel='next']",
    },
    "product_detail": {
        "sku": ".sku, .codigo, .ref",
        "name": "h1, .product-name",
        "description": ".description, .descricao",
        "photos": ".gallery img, .product-images img, .fotos img",
    },
}


@register_connector("pellegrino")
class PellegrinoConnector(BaseConnector):
    """Pellegrino connector — photos and description only, stock unavailable."""

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
        await self._page.goto(f"{BASE_URL}/login", wait_until="networkidle", timeout=30000)
        await self._human_delay(0.5, 1.5)

        await self._page.locator(SELECTORS["login"]["username"]).first.fill(self.credentials["login"])
        await self._human_delay(0.3, 0.8)
        await self._page.locator(SELECTORS["login"]["password"]).first.fill(self.credentials["password"])
        await self._human_delay(0.3, 0.8)
        await self._page.locator(SELECTORS["login"]["submit"]).first.click()
        await self._page.wait_for_load_state("networkidle", timeout=15000)

        if "login" in self._page.url.lower():
            raise ConnectionError("Login Pellegrino falhou")

        logger.info("Pellegrino login successful")
        return True

    @retry(max_attempts=3, backoff=[5, 15, 45])
    async def fetch_catalog(self) -> list[ProductData]:
        if not self._page:
            raise RuntimeError("Not authenticated")

        products = []
        await self._page.goto(f"{BASE_URL}/produtos", wait_until="networkidle", timeout=30000)
        await self._human_delay()

        page_num = 1
        while True:
            logger.info("Pellegrino: scraping page %d", page_num)
            try:
                await self._page.wait_for_selector(SELECTORS["catalog"]["product_list"], timeout=10000)
            except Exception:
                break

            product_links = []
            link_els = await self._page.locator(SELECTORS["catalog"]["product_link"]).all()
            for link_el in link_els:
                href = await link_el.get_attribute("href")
                if href:
                    product_links.append(href)

            for href in product_links:
                try:
                    url = href if href.startswith("http") else f"{BASE_URL}{href}"
                    await self._page.goto(url, wait_until="networkidle", timeout=30000)
                    await self._human_delay(0.5, 1.0)

                    async def safe_text(sel):
                        el = self._page.locator(sel).first
                        if await el.count():
                            return (await el.text_content() or "").strip()
                        return None

                    sku = await safe_text(SELECTORS["product_detail"]["sku"])
                    name = await safe_text(SELECTORS["product_detail"]["name"])
                    if not sku or not name:
                        continue

                    description = await safe_text(SELECTORS["product_detail"]["description"])

                    photos = []
                    for img in await self._page.locator(SELECTORS["product_detail"]["photos"]).all():
                        src = await img.get_attribute("src")
                        if src:
                            photos.append(src if src.startswith("http") else f"{BASE_URL}{src}")

                    products.append(ProductData(
                        sku=sku,
                        name=name,
                        description=description,
                        stock_quantity=None,  # Stock unavailable for Pellegrino
                        photos=photos,
                        raw_data={"source_url": url},
                    ))
                except Exception as exc:
                    logger.warning("Pellegrino: failed to extract %s: %s", href, exc)

            next_btn = self._page.locator(SELECTORS["catalog"]["next_page"]).first
            if await next_btn.count() and await next_btn.is_enabled():
                await next_btn.click()
                await self._page.wait_for_load_state("networkidle", timeout=15000)
                await self._human_delay()
                page_num += 1
            else:
                break

        logger.info("Pellegrino: extracted %d products (no stock)", len(products))
        return products

    async def fetch_stock(self) -> dict[str, int | None]:
        return {}

    async def health_check(self) -> dict:
        try:
            if not self._page:
                await self._init_browser()
            await self._page.goto(BASE_URL, wait_until="domcontentloaded", timeout=15000)
            return {"status": "ok", "url": BASE_URL}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    async def close(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._browser = self._page = self._playwright = None

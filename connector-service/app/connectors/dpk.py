import asyncio
import logging
import random

from playwright.async_api import async_playwright, Browser, Page

from app.connectors.base import BaseConnector, ProductData, retry
from app.connectors.registry import register_connector

logger = logging.getLogger(__name__)

SELECTORS = {
    "login": {
        "username": 'input[type="email"], input[name="email"], #email',
        "password": 'input[type="password"], input[name="password"], #password',
        "submit": 'button[type="submit"], input[type="submit"], .btn-login',
    },
    "catalog": {
        "product_list": ".product-card, .product-item, tr.product-row",
        "product_link": "a[href*='product'], a[href*='detalhe'], a.product-link",
        "next_page": ".pagination .next, a[rel='next'], .page-next",
    },
    "product_detail": {
        "sku": ".product-sku, .sku, [data-sku]",
        "name": "h1, .product-name, .product-title",
        "description": ".product-description, .description, .product-detail",
        "price": ".product-price, .price, .valor",
        "stock": ".stock-quantity, .estoque, .stock",
        "weight": ".weight, .peso",
        "dimensions": ".dimensions, .medidas",
        "photos": "img.product-photo, .product-gallery img, .photos img",
    },
}

BASE_URL = "https://www.dpk.com.br"


@register_connector("dpk")
class DPKConnector(BaseConnector):
    def __init__(self, credentials: dict, settings: dict | None = None):
        super().__init__(credentials, settings)
        self._browser: Browser | None = None
        self._page: Page | None = None
        self._playwright = None

    async def _init_browser(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
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

        await self._page.goto(f"{BASE_URL}/#/login", wait_until="networkidle", timeout=30000)
        await self._human_delay(0.5, 1.5)

        # Fill login form
        login_input = self._page.locator(SELECTORS["login"]["username"]).first
        await login_input.fill(self.credentials["login"])
        await self._human_delay(0.3, 0.8)

        password_input = self._page.locator(SELECTORS["login"]["password"]).first
        await password_input.fill(self.credentials["password"])
        await self._human_delay(0.3, 0.8)

        submit_btn = self._page.locator(SELECTORS["login"]["submit"]).first
        await submit_btn.click()

        # Wait for navigation after login
        await self._page.wait_for_load_state("networkidle", timeout=15000)
        await self._human_delay()

        # Verify login succeeded (URL should change from /login)
        current_url = self._page.url
        if "login" in current_url.lower():
            # Check for error message
            error_el = self._page.locator(".error, .alert-danger, .login-error").first
            error_msg = await error_el.text_content() if await error_el.count() else "URL ainda na página de login"
            raise ConnectionError(f"Login DPK falhou: {error_msg}")

        logger.info("DPK login successful")
        return True

    @retry(max_attempts=3, backoff=[5, 15, 45])
    async def fetch_catalog(self) -> list[ProductData]:
        if not self._page:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        products = []

        # Navigate to catalog
        await self._page.goto(f"{BASE_URL}/#/produtos", wait_until="networkidle", timeout=30000)
        await self._human_delay()

        page_num = 1
        while True:
            logger.info("DPK: scraping page %d", page_num)

            # Wait for product list to load
            await self._page.wait_for_selector(
                SELECTORS["catalog"]["product_list"], timeout=15000
            )

            # Get product links on this page
            product_elements = await self._page.locator(SELECTORS["catalog"]["product_list"]).all()

            if not product_elements:
                logger.warning("DPK: no products found on page %d", page_num)
                break

            # Collect product links first
            product_links = []
            for el in product_elements:
                link = el.locator(SELECTORS["catalog"]["product_link"]).first
                if await link.count():
                    href = await link.get_attribute("href")
                    if href:
                        product_links.append(href)

            # Visit each product detail page
            for href in product_links:
                try:
                    product = await self._extract_product_detail(href)
                    if product:
                        products.append(product)
                except Exception as exc:
                    logger.warning("DPK: failed to extract product %s: %s", href, exc)

                await self._human_delay(0.5, 1.5)

            # Check for next page
            next_btn = self._page.locator(SELECTORS["catalog"]["next_page"]).first
            if await next_btn.count() and await next_btn.is_enabled():
                await next_btn.click()
                await self._page.wait_for_load_state("networkidle", timeout=15000)
                await self._human_delay()
                page_num += 1
            else:
                break

        logger.info("DPK: extracted %d products total", len(products))
        return products

    async def _extract_product_detail(self, href: str) -> ProductData | None:
        url = href if href.startswith("http") else f"{BASE_URL}{href}"
        await self._page.goto(url, wait_until="networkidle", timeout=30000)
        await self._human_delay(0.5, 1.0)

        async def safe_text(selector: str) -> str | None:
            el = self._page.locator(selector).first
            if await el.count():
                return (await el.text_content() or "").strip()
            return None

        sku = await safe_text(SELECTORS["product_detail"]["sku"])
        name = await safe_text(SELECTORS["product_detail"]["name"])
        if not sku or not name:
            return None

        description = await safe_text(SELECTORS["product_detail"]["description"])

        price_text = await safe_text(SELECTORS["product_detail"]["price"])
        price = self._parse_price(price_text) if price_text else None

        stock_text = await safe_text(SELECTORS["product_detail"]["stock"])
        stock = self._parse_int(stock_text) if stock_text else None

        weight_text = await safe_text(SELECTORS["product_detail"]["weight"])
        weight = self._parse_float(weight_text) if weight_text else None

        dimensions = await safe_text(SELECTORS["product_detail"]["dimensions"])
        height, width, length = self._parse_dimensions(dimensions) if dimensions else (None, None, None)

        # Extract photo URLs
        photo_elements = await self._page.locator(SELECTORS["product_detail"]["photos"]).all()
        photos = []
        for img in photo_elements:
            src = await img.get_attribute("src")
            if src:
                photos.append(src if src.startswith("http") else f"{BASE_URL}{src}")

        return ProductData(
            sku=sku,
            name=name,
            description=description,
            price=price,
            stock_quantity=stock,
            weight=weight,
            height=height,
            width=width,
            length=length,
            photos=photos,
            raw_data={"source_url": url},
        )

    async def fetch_stock(self) -> dict[str, int | None]:
        catalog = await self.fetch_catalog()
        return {p.sku: p.stock_quantity for p in catalog}

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
        self._browser = None
        self._page = None
        self._playwright = None

    @staticmethod
    def _parse_price(text: str) -> float | None:
        import re
        clean = re.sub(r"[^\d,.]", "", text)
        clean = clean.replace(".", "").replace(",", ".")
        try:
            return float(clean)
        except ValueError:
            return None

    @staticmethod
    def _parse_int(text: str) -> int | None:
        import re
        digits = re.sub(r"\D", "", text)
        return int(digits) if digits else None

    @staticmethod
    def _parse_float(text: str) -> float | None:
        import re
        clean = re.sub(r"[^\d,.]", "", text)
        clean = clean.replace(",", ".")
        try:
            return float(clean)
        except ValueError:
            return None

    @staticmethod
    def _parse_dimensions(text: str) -> tuple[float | None, float | None, float | None]:
        import re
        numbers = re.findall(r"[\d.,]+", text)
        numbers = [float(n.replace(",", ".")) for n in numbers]
        if len(numbers) >= 3:
            return numbers[0], numbers[1], numbers[2]
        return None, None, None

import asyncio
import logging
import random

from playwright.async_api import async_playwright, Browser, Page

from app.connectors.base import BaseConnector, ProductData, retry
from app.connectors.registry import register_connector

logger = logging.getLogger(__name__)

SELECTORS = {
    "login": {
        "username": 'input[name="login"], input[type="email"], #login',
        "password": 'input[name="senha"], input[type="password"], #senha',
        "submit": 'button[type="submit"], .btn-entrar',
    },
    "catalog": {
        "product_list": ".product-item, tr.produto, .card-produto",
        "product_link": "a[href*='produto'], a.link-produto",
        "next_page": ".pagination .next, a.proxima",
    },
    "product_detail": {
        "sku": ".codigo, .sku, .ref",
        "name": "h1, .nome-produto",
        "description": ".descricao, .description",
        "price": ".preco, .valor, .price",
        "stock": ".estoque, .disponivel",
        "weight": ".peso",
        "dimensions": ".dimensoes, .medidas",
        "photos": ".galeria img, .fotos img, .product-image img",
    },
}

BASE_URL = "https://vendas.furacao.com.br"


@register_connector("furacao")
class FuracaoConnector(BaseConnector):
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
        await self._page.goto(f"{BASE_URL}/vendas/login", wait_until="networkidle", timeout=30000)
        await self._human_delay(0.5, 1.5)

        await self._page.locator(SELECTORS["login"]["username"]).first.fill(self.credentials["login"])
        await self._human_delay(0.3, 0.8)
        await self._page.locator(SELECTORS["login"]["password"]).first.fill(self.credentials["password"])
        await self._human_delay(0.3, 0.8)
        await self._page.locator(SELECTORS["login"]["submit"]).first.click()
        await self._page.wait_for_load_state("networkidle", timeout=15000)

        if "login" in self._page.url.lower():
            raise ConnectionError("Login Furacão falhou: credenciais inválidas ou página de login não redirecionou")

        logger.info("Furacão login successful")
        return True

    @retry(max_attempts=3, backoff=[5, 15, 45])
    async def fetch_catalog(self) -> list[ProductData]:
        if not self._page:
            raise RuntimeError("Not authenticated")

        products = []
        await self._page.goto(f"{BASE_URL}/vendas/sav/produtos", wait_until="networkidle", timeout=30000)
        await self._human_delay()

        page_num = 1
        while True:
            logger.info("Furacão: scraping page %d", page_num)
            await self._page.wait_for_selector(SELECTORS["catalog"]["product_list"], timeout=15000)
            product_elements = await self._page.locator(SELECTORS["catalog"]["product_list"]).all()

            if not product_elements:
                break

            for el in product_elements:
                try:
                    product = await self._extract_from_element(el)
                    if product:
                        products.append(product)
                except Exception as exc:
                    logger.warning("Furacão: failed to extract product: %s", exc)

            next_btn = self._page.locator(SELECTORS["catalog"]["next_page"]).first
            if await next_btn.count() and await next_btn.is_enabled():
                await next_btn.click()
                await self._page.wait_for_load_state("networkidle", timeout=15000)
                await self._human_delay()
                page_num += 1
            else:
                break

        logger.info("Furacão: extracted %d products", len(products))
        return products

    async def _extract_from_element(self, el) -> ProductData | None:
        async def safe_text(selector: str) -> str | None:
            loc = el.locator(selector).first
            if await loc.count():
                return (await loc.text_content() or "").strip()
            return None

        sku = await safe_text(SELECTORS["product_detail"]["sku"])
        name = await safe_text(SELECTORS["product_detail"]["name"])
        if not sku or not name:
            return None

        from app.connectors.dpk import DPKConnector
        price_text = await safe_text(SELECTORS["product_detail"]["price"])
        stock_text = await safe_text(SELECTORS["product_detail"]["stock"])

        photos = []
        photo_els = await el.locator(SELECTORS["product_detail"]["photos"]).all()
        for img in photo_els:
            src = await img.get_attribute("src")
            if src:
                photos.append(src if src.startswith("http") else f"{BASE_URL}{src}")

        return ProductData(
            sku=sku,
            name=name,
            description=await safe_text(SELECTORS["product_detail"]["description"]),
            price=DPKConnector._parse_price(price_text) if price_text else None,
            stock_quantity=DPKConnector._parse_int(stock_text) if stock_text else None,
            photos=photos,
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
        self._browser = self._page = self._playwright = None

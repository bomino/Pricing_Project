import asyncio
import re
from typing import Optional, List, Dict, Any
from .base import ScraperProviderAdapter, MaterialPrice, SyncResult
from .registry import provider_registry


class PlaywrightScraperAdapter(ScraperProviderAdapter):
    """
    Generic web scraper adapter using Playwright for ethical web scraping.

    This adapter provides a framework for scraping public pricing data
    with proper rate limiting and robots.txt compliance.

    Required config:
    - base_url: Target website URL
    - selectors: CSS selectors for data extraction
    - respect_robots_txt: Whether to check robots.txt (default: True)
    - delay_seconds: Delay between requests (default: 2)

    Example selectors config:
    {
        "product_list": ".product-grid .product-item",
        "name": ".product-title",
        "price": ".product-price",
        "unit": ".product-unit",
        "link": "a.product-link",
        "next_page": ".pagination .next"
    }
    """

    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.selectors = self.config.get('selectors', {})
        self.headless = self.config.get('headless', True)
        self.max_pages = self.config.get('max_pages', 5)
        self._browser = None
        self._page = None

    async def _get_browser(self):
        if self._browser is None:
            try:
                from playwright.async_api import async_playwright
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(headless=self.headless)
            except ImportError:
                raise ImportError("Playwright is required. Install with: pip install playwright && playwright install chromium")
        return self._browser

    async def _get_page(self):
        if self._page is None or self._page.is_closed():
            browser = await self._get_browser()
            self._page = await browser.new_page()
            await self._page.set_extra_http_headers({
                'User-Agent': 'MaterialsSearch/1.0 (Research Bot; +https://example.com/bot)'
            })
        return self._page

    async def close(self):
        if self._page and not self._page.is_closed():
            await self._page.close()
        if self._browser:
            await self._browser.close()
        if hasattr(self, '_playwright'):
            await self._playwright.stop()

    async def fetch_prices(
        self,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 100
    ) -> SyncResult:
        if not await self.check_robots_txt():
            return SyncResult(
                success=False,
                items_processed=0,
                items_failed=0,
                error_message='Scraping disallowed by robots.txt'
            )

        try:
            page = await self._get_page()
            all_prices = []
            pages_scraped = 0
            failed_items = 0

            search_url = self._build_search_url(category, search_query)
            await page.goto(search_url, wait_until='networkidle')

            while pages_scraped < self.max_pages and len(all_prices) < limit:
                await asyncio.sleep(self.delay_between_requests)

                items = await self._extract_items(page)
                for item in items:
                    try:
                        price = self._parse_item(item)
                        if price:
                            all_prices.append(price)
                    except Exception:
                        failed_items += 1

                    if len(all_prices) >= limit:
                        break

                pages_scraped += 1

                if pages_scraped < self.max_pages and len(all_prices) < limit:
                    has_next = await self._go_to_next_page(page)
                    if not has_next:
                        break

            return SyncResult(
                success=True,
                items_processed=len(all_prices),
                items_failed=failed_items,
                prices=all_prices
            )

        except Exception as e:
            return SyncResult(
                success=False,
                items_processed=0,
                items_failed=0,
                error_message=str(e)
            )

    async def fetch_single_price(self, external_id: str) -> Optional[MaterialPrice]:
        try:
            page = await self._get_page()
            product_url = f"{self.base_url}/product/{external_id}"
            await page.goto(product_url, wait_until='networkidle')

            item = await self._extract_single_item(page)
            return self._parse_item(item) if item else None

        except Exception:
            return None

    async def search_materials(self, query: str, limit: int = 20) -> List[MaterialPrice]:
        result = await self.fetch_prices(search_query=query, limit=limit)
        return result.prices or []

    async def validate_connection(self) -> bool:
        try:
            page = await self._get_page()
            response = await page.goto(self.base_url, wait_until='domcontentloaded')
            return response.status < 400
        except Exception:
            return False

    def _build_search_url(self, category: Optional[str], search_query: Optional[str]) -> str:
        url_template = self.config.get('search_url_template', '{base_url}/search?q={query}')
        query = search_query or category or ''
        return url_template.format(base_url=self.base_url, query=query, category=category or '')

    async def _extract_items(self, page) -> List[Dict[str, Any]]:
        items = []
        product_selector = self.selectors.get('product_list', '.product-item')

        try:
            elements = await page.query_selector_all(product_selector)

            for el in elements:
                item = {}

                for field, selector in self.selectors.items():
                    if field == 'product_list' or field == 'next_page':
                        continue

                    try:
                        field_el = await el.query_selector(selector)
                        if field_el:
                            if field == 'link':
                                item[field] = await field_el.get_attribute('href')
                            else:
                                item[field] = await field_el.inner_text()
                    except Exception:
                        pass

                if item.get('name') and item.get('price'):
                    items.append(item)

        except Exception:
            pass

        return items

    async def _extract_single_item(self, page) -> Optional[Dict[str, Any]]:
        item = {}
        detail_selectors = self.config.get('detail_selectors', self.selectors)

        for field, selector in detail_selectors.items():
            if field in ('product_list', 'next_page'):
                continue

            try:
                el = await page.query_selector(selector)
                if el:
                    if field == 'link':
                        item[field] = await page.url
                    else:
                        item[field] = await el.inner_text()
            except Exception:
                pass

        return item if item.get('name') and item.get('price') else None

    async def _go_to_next_page(self, page) -> bool:
        next_selector = self.selectors.get('next_page', '.pagination .next')
        try:
            next_btn = await page.query_selector(next_selector)
            if next_btn and await next_btn.is_visible():
                await next_btn.click()
                await page.wait_for_load_state('networkidle')
                return True
        except Exception:
            pass
        return False

    def _parse_item(self, item: Dict[str, Any]) -> Optional[MaterialPrice]:
        if not item.get('name') or not item.get('price'):
            return None

        try:
            price_str = item.get('price', '0')
            price_value = self._parse_price(price_str)

            external_id = item.get('id') or item.get('sku') or self._generate_id(item.get('name', ''))

            return MaterialPrice(
                external_id=str(external_id),
                name=item.get('name', '').strip(),
                price=price_value,
                unit=self._parse_unit(item.get('unit', ''), item.get('name', '')),
                currency='USD',
                confidence_score=0.7,
                source_url=self._make_absolute_url(item.get('link', '')),
                category=item.get('category', self._infer_category(item.get('name', ''))),
                raw_data=item,
                specifications={
                    'scraped': True,
                    'source': self.name
                }
            )

        except Exception:
            return None

    def _parse_price(self, price_str: str) -> float:
        if not price_str:
            return 0.0

        cleaned = re.sub(r'[^\d.,]', '', str(price_str))
        cleaned = cleaned.replace(',', '')

        match = re.search(r'(\d+\.?\d*)', cleaned)
        if match:
            return float(match.group(1))

        return 0.0

    def _parse_unit(self, unit_str: str, name: str) -> str:
        unit_lower = (unit_str or '').lower()
        name_lower = name.lower()

        unit_patterns = {
            'SF': ['sq ft', 'sq. ft', 'square foot', 'sqft', '/sf'],
            'LF': ['lin ft', 'lin. ft', 'linear foot', 'lf', '/lf'],
            'CY': ['cu yd', 'cubic yard', 'cy'],
            'BAG': ['bag', '/bag', 'per bag'],
            'SHT': ['sheet', '/sheet', 'per sheet'],
            'GAL': ['gallon', 'gal', '/gal'],
            'BOX': ['box', '/box', 'per box'],
            'CS': ['case', '/case', 'per case'],
            'BDL': ['bundle', '/bundle', 'per bundle']
        }

        combined = f"{unit_lower} {name_lower}"
        for unit, patterns in unit_patterns.items():
            if any(p in combined for p in patterns):
                return unit

        return 'EA'

    def _generate_id(self, name: str) -> str:
        import hashlib
        return hashlib.md5(name.encode()).hexdigest()[:12]

    def _make_absolute_url(self, url: str) -> str:
        if not url:
            return ''
        if url.startswith('http'):
            return url
        if url.startswith('/'):
            return f"{self.base_url.rstrip('/')}{url}"
        return f"{self.base_url.rstrip('/')}/{url}"

    def _infer_category(self, title: str) -> str:
        title_lower = title.lower()
        categories = {
            'Lumber': ['lumber', 'wood', 'plywood', '2x4', '2x6', 'stud', 'board'],
            'Concrete': ['concrete', 'cement', 'mortar'],
            'Steel': ['steel', 'rebar', 'metal'],
            'Drywall': ['drywall', 'sheetrock', 'gypsum'],
            'Insulation': ['insulation', 'foam'],
            'Roofing': ['shingle', 'roofing'],
            'Plumbing': ['pipe', 'pvc', 'fitting'],
            'Electrical': ['wire', 'electrical', 'outlet']
        }

        for cat, keywords in categories.items():
            if any(kw in title_lower for kw in keywords):
                return cat

        return 'General'


class GraingerScraperAdapter(PlaywrightScraperAdapter):
    """Pre-configured scraper for Grainger industrial supplies."""

    def __init__(self, provider_config: Dict[str, Any]):
        provider_config['base_url'] = provider_config.get('base_url', 'https://www.grainger.com')
        provider_config['config'] = provider_config.get('config', {})
        provider_config['config']['selectors'] = {
            'product_list': '[data-testid="product-card"]',
            'name': '[data-testid="product-title"]',
            'price': '[data-testid="product-price"]',
            'link': 'a[data-testid="product-link"]',
            'next_page': '[data-testid="pagination-next"]'
        }
        provider_config['config']['search_url_template'] = '{base_url}/search?searchQuery={query}'
        super().__init__(provider_config)


class MCMasterScraperAdapter(PlaywrightScraperAdapter):
    """Pre-configured scraper for McMaster-Carr industrial supplies."""

    def __init__(self, provider_config: Dict[str, Any]):
        provider_config['base_url'] = provider_config.get('base_url', 'https://www.mcmaster.com')
        provider_config['config'] = provider_config.get('config', {})
        provider_config['config']['selectors'] = {
            'product_list': '.ProductSumm',
            'name': '.ProductDesc',
            'price': '.PrcePrcng',
            'link': 'a',
            'next_page': '.NextPageLink'
        }
        provider_config['config']['search_url_template'] = '{base_url}/{query}'
        super().__init__(provider_config)


provider_registry.register('playwright_scraper', PlaywrightScraperAdapter)
provider_registry.register('grainger', GraingerScraperAdapter)
provider_registry.register('mcmaster', MCMasterScraperAdapter)

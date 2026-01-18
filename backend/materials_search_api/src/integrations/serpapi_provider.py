from typing import Optional, List, Dict, Any
from .base import APIProviderAdapter, MaterialPrice, SyncResult
from .registry import provider_registry


class SerpApiProviderAdapter(APIProviderAdapter):
    """
    SerpApi adapter for fetching retail pricing from Home Depot, Lowe's, etc.

    SerpApi provides structured search results from:
    - Home Depot (home_depot)
    - Lowe's (lowes)
    - Google Shopping (google_shopping)

    API Documentation: https://serpapi.com/

    Required config:
    - api_key: SerpApi API key
    - base_url: https://serpapi.com (default)
    - engine: Search engine ('home_depot', 'lowes', 'google_shopping')
    """

    def __init__(self, provider_config: Dict[str, Any]):
        if not provider_config.get('base_url'):
            provider_config['base_url'] = 'https://serpapi.com'
        super().__init__(provider_config)
        self.engine = self.config.get('engine', 'home_depot')
        self.location = self.config.get('location', 'United States')

    def _get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': 'MaterialsSearch/1.0',
            'Accept': 'application/json'
        }

    async def fetch_prices(
        self,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 100
    ) -> SyncResult:
        try:
            query = search_query or category or 'construction materials'
            client = await self.get_client()

            params = {
                'api_key': self.api_key,
                'engine': self.engine,
                'q': query,
                'num': min(limit, 100)
            }

            if self.engine == 'home_depot':
                params['delivery_zip'] = self.config.get('zip_code', '45409')
            elif self.engine == 'google_shopping':
                params['location'] = self.location
                params['gl'] = 'us'
                params['hl'] = 'en'

            response = await client.get('/search.json', params=params)

            if response.status_code == 401:
                return SyncResult(
                    success=False,
                    items_processed=0,
                    items_failed=0,
                    error_message='Invalid API key'
                )

            if response.status_code != 200:
                return SyncResult(
                    success=False,
                    items_processed=0,
                    items_failed=0,
                    error_message=f'API error: {response.status_code}'
                )

            data = response.json()
            prices = self._parse_response(data, category)

            return SyncResult(
                success=True,
                items_processed=len(prices),
                items_failed=0,
                prices=prices
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
            client = await self.get_client()

            if self.engine == 'home_depot':
                params = {
                    'api_key': self.api_key,
                    'engine': 'home_depot_product',
                    'product_id': external_id,
                    'delivery_zip': self.config.get('zip_code', '45409')
                }
            else:
                return None

            response = await client.get('/search.json', params=params)

            if response.status_code != 200:
                return None

            data = response.json()
            product = data.get('product_results', {})

            if not product:
                return None

            return self._parse_product(product)

        except Exception:
            return None

    async def search_materials(self, query: str, limit: int = 20) -> List[MaterialPrice]:
        result = await self.fetch_prices(search_query=query, limit=limit)
        return result.prices or []

    async def validate_connection(self) -> bool:
        try:
            client = await self.get_client()
            params = {
                'api_key': self.api_key,
                'engine': self.engine,
                'q': 'test',
                'num': 1
            }
            response = await client.get('/search.json', params=params)
            return response.status_code == 200
        except Exception:
            return False

    def _parse_response(self, data: Dict[str, Any], category: Optional[str]) -> List[MaterialPrice]:
        prices = []

        if self.engine == 'home_depot':
            items = data.get('products', [])
            for item in items:
                price = self._parse_home_depot_item(item, category)
                if price:
                    prices.append(price)

        elif self.engine == 'lowes':
            items = data.get('organic_results', [])
            for item in items:
                price = self._parse_lowes_item(item, category)
                if price:
                    prices.append(price)

        elif self.engine == 'google_shopping':
            items = data.get('shopping_results', [])
            for item in items:
                price = self._parse_google_shopping_item(item, category)
                if price:
                    prices.append(price)

        return prices

    def _parse_home_depot_item(self, item: Dict[str, Any], category: Optional[str]) -> Optional[MaterialPrice]:
        try:
            price_value = item.get('price', 0)
            if isinstance(price_value, str):
                price_value = float(price_value.replace('$', '').replace(',', ''))

            return MaterialPrice(
                external_id=str(item.get('product_id', item.get('model', ''))),
                name=item.get('title', ''),
                price=price_value,
                unit=self._extract_unit(item.get('title', ''), item.get('unit', 'EA')),
                currency='USD',
                confidence_score=0.85,
                source_url=item.get('link', ''),
                category=category or self._infer_category(item.get('title', '')),
                raw_data=item,
                specifications={
                    'brand': item.get('brand'),
                    'model': item.get('model'),
                    'rating': item.get('rating'),
                    'reviews': item.get('reviews'),
                    'in_stock': item.get('in_stock', True),
                    'delivery': item.get('delivery'),
                    'store': 'Home Depot'
                }
            )
        except (ValueError, KeyError):
            return None

    def _parse_lowes_item(self, item: Dict[str, Any], category: Optional[str]) -> Optional[MaterialPrice]:
        try:
            price_str = item.get('price', '0')
            if isinstance(price_str, str):
                price_value = float(price_str.replace('$', '').replace(',', '').split()[0])
            else:
                price_value = float(price_str)

            return MaterialPrice(
                external_id=str(item.get('product_id', item.get('position', ''))),
                name=item.get('title', ''),
                price=price_value,
                unit=self._extract_unit(item.get('title', ''), 'EA'),
                currency='USD',
                confidence_score=0.85,
                source_url=item.get('link', ''),
                category=category or self._infer_category(item.get('title', '')),
                raw_data=item,
                specifications={
                    'rating': item.get('rating'),
                    'reviews': item.get('reviews'),
                    'store': 'Lowes'
                }
            )
        except (ValueError, KeyError):
            return None

    def _parse_google_shopping_item(self, item: Dict[str, Any], category: Optional[str]) -> Optional[MaterialPrice]:
        try:
            price_str = item.get('extracted_price', item.get('price', '0'))
            if isinstance(price_str, str):
                price_value = float(price_str.replace('$', '').replace(',', ''))
            else:
                price_value = float(price_str)

            return MaterialPrice(
                external_id=str(item.get('product_id', item.get('position', ''))),
                name=item.get('title', ''),
                price=price_value,
                unit=self._extract_unit(item.get('title', ''), 'EA'),
                currency='USD',
                confidence_score=0.75,
                source_url=item.get('link', ''),
                category=category or self._infer_category(item.get('title', '')),
                raw_data=item,
                specifications={
                    'source': item.get('source'),
                    'rating': item.get('rating'),
                    'reviews': item.get('reviews'),
                    'shipping': item.get('shipping'),
                    'store': item.get('source', 'Google Shopping')
                }
            )
        except (ValueError, KeyError):
            return None

    def _parse_product(self, product: Dict[str, Any]) -> Optional[MaterialPrice]:
        try:
            price_value = product.get('price', 0)
            if isinstance(price_value, str):
                price_value = float(price_value.replace('$', '').replace(',', ''))

            return MaterialPrice(
                external_id=str(product.get('product_id', '')),
                name=product.get('title', ''),
                price=price_value,
                unit=self._extract_unit(product.get('title', ''), 'EA'),
                currency='USD',
                confidence_score=0.9,
                source_url=product.get('link', ''),
                category=self._infer_category(product.get('title', '')),
                raw_data=product,
                specifications={
                    'brand': product.get('brand'),
                    'model': product.get('model'),
                    'description': product.get('description'),
                    'specifications': product.get('specifications'),
                    'store': 'Home Depot'
                }
            )
        except (ValueError, KeyError):
            return None

    def _extract_unit(self, title: str, default: str = 'EA') -> str:
        title_lower = title.lower()
        unit_patterns = {
            '/sq. ft': 'SF',
            '/sq ft': 'SF',
            'per sq ft': 'SF',
            '/lin. ft': 'LF',
            '/lin ft': 'LF',
            '/linear ft': 'LF',
            'per linear': 'LF',
            '/cu. yd': 'CY',
            '/cu yd': 'CY',
            'per bag': 'BAG',
            '/bag': 'BAG',
            '/sheet': 'SHT',
            'per sheet': 'SHT',
            '/piece': 'EA',
            '/each': 'EA',
            'per piece': 'EA',
            '/box': 'BOX',
            'per box': 'BOX',
            '/case': 'CS',
            'per case': 'CS',
            '/bundle': 'BDL',
            'per bundle': 'BDL',
            '/gallon': 'GAL',
            '/gal': 'GAL',
            'per gallon': 'GAL'
        }

        for pattern, unit in unit_patterns.items():
            if pattern in title_lower:
                return unit

        return default

    def _infer_category(self, title: str) -> str:
        title_lower = title.lower()
        category_keywords = {
            'Lumber': ['lumber', 'wood', 'plywood', 'osb', '2x4', '2x6', '2x8', '2x10', '2x12', 'stud'],
            'Concrete': ['concrete', 'cement', 'mortar', 'grout'],
            'Steel': ['steel', 'rebar', 'metal', 'iron', 'aluminum'],
            'Drywall': ['drywall', 'sheetrock', 'gypsum'],
            'Insulation': ['insulation', 'foam', 'fiberglass', 'r-value'],
            'Roofing': ['shingle', 'roofing', 'roof', 'underlayment'],
            'Flooring': ['flooring', 'tile', 'hardwood', 'laminate', 'vinyl'],
            'Plumbing': ['pipe', 'pvc', 'fitting', 'valve', 'plumbing', 'faucet'],
            'Electrical': ['wire', 'electrical', 'outlet', 'switch', 'breaker', 'conduit'],
            'Hardware': ['nail', 'screw', 'bolt', 'fastener', 'hinge', 'bracket'],
            'Paint': ['paint', 'primer', 'stain', 'sealer'],
            'Doors & Windows': ['door', 'window', 'frame']
        }

        for category, keywords in category_keywords.items():
            if any(kw in title_lower for kw in keywords):
                return category

        return 'General'


class HomeDepotProviderAdapter(SerpApiProviderAdapter):
    """Convenience class for Home Depot specifically."""

    def __init__(self, provider_config: Dict[str, Any]):
        provider_config['config'] = provider_config.get('config', {})
        provider_config['config']['engine'] = 'home_depot'
        super().__init__(provider_config)


class LowesProviderAdapter(SerpApiProviderAdapter):
    """Convenience class for Lowe's specifically."""

    def __init__(self, provider_config: Dict[str, Any]):
        provider_config['config'] = provider_config.get('config', {})
        provider_config['config']['engine'] = 'lowes'
        super().__init__(provider_config)


provider_registry.register('serpapi', SerpApiProviderAdapter)
provider_registry.register('home_depot', HomeDepotProviderAdapter)
provider_registry.register('lowes', LowesProviderAdapter)

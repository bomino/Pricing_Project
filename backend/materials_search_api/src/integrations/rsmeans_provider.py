from typing import Optional, List, Dict, Any
from .base import APIProviderAdapter, MaterialPrice, SyncResult
from .registry import provider_registry


class RSMeansProviderAdapter(APIProviderAdapter):
    """
    RSMeans API adapter for construction cost data.

    RSMeans provides comprehensive construction cost data including:
    - Material costs
    - Labor costs
    - Equipment costs
    - Regional cost adjustments

    API Documentation: https://www.rsmeans.com/api

    Required config:
    - api_key: RSMeans API key
    - base_url: https://api.rsmeans.com/v1 (default)
    - region_code: Geographic region for pricing (e.g., 'US-OH' for Ohio)
    """

    def __init__(self, provider_config: Dict[str, Any]):
        if not provider_config.get('base_url'):
            provider_config['base_url'] = 'https://api.rsmeans.com/v1'
        super().__init__(provider_config)
        self.region_code = self.config.get('region_code', 'US-NATL')
        self.data_year = self.config.get('data_year', '2024')

    def _get_headers(self) -> Dict[str, str]:
        headers = super()._get_headers()
        if self.api_key:
            headers['X-API-Key'] = self.api_key
            headers['Authorization'] = f'Bearer {self.api_key}'
        headers['Accept'] = 'application/json'
        return headers

    async def fetch_prices(
        self,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 100
    ) -> SyncResult:
        try:
            client = await self.get_client()

            params = {
                'limit': min(limit, 100),
                'region': self.region_code,
                'year': self.data_year
            }

            if category:
                params['division'] = self._map_category_to_division(category)
            if search_query:
                params['search'] = search_query

            response = await client.get('/costs/materials', params=params)

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
            prices = self._parse_response(data)

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

            response = await client.get(
                f'/costs/materials/{external_id}',
                params={'region': self.region_code, 'year': self.data_year}
            )

            if response.status_code != 200:
                return None

            data = response.json()
            prices = self._parse_response({'items': [data]})
            return prices[0] if prices else None

        except Exception:
            return None

    async def search_materials(self, query: str, limit: int = 20) -> List[MaterialPrice]:
        result = await self.fetch_prices(search_query=query, limit=limit)
        return result.prices or []

    async def validate_connection(self) -> bool:
        try:
            client = await self.get_client()
            response = await client.get('/status')
            return response.status_code == 200
        except Exception:
            return False

    def _parse_response(self, data: Dict[str, Any]) -> List[MaterialPrice]:
        prices = []
        items = data.get('items', data.get('data', []))

        for item in items:
            try:
                price = MaterialPrice(
                    external_id=item.get('id', item.get('code', '')),
                    name=item.get('description', item.get('name', '')),
                    price=float(item.get('unit_cost', item.get('material_cost', 0))),
                    unit=item.get('unit', 'EA'),
                    currency='USD',
                    confidence_score=0.95,
                    source_url=f"https://www.rsmeans.com/costs/{item.get('id', '')}",
                    category=self._map_division_to_category(item.get('division', '')),
                    raw_data=item,
                    specifications={
                        'division': item.get('division'),
                        'subdivision': item.get('subdivision'),
                        'labor_cost': item.get('labor_cost'),
                        'equipment_cost': item.get('equipment_cost'),
                        'total_cost': item.get('total_cost'),
                        'crew': item.get('crew'),
                        'daily_output': item.get('daily_output'),
                        'region': self.region_code
                    }
                )
                prices.append(price)
            except (ValueError, KeyError):
                continue

        return prices

    def _map_category_to_division(self, category: str) -> str:
        division_map = {
            'Concrete': '03',
            'Masonry': '04',
            'Metals': '05',
            'Steel': '05',
            'Wood': '06',
            'Lumber': '06',
            'Thermal': '07',
            'Insulation': '07',
            'Doors': '08',
            'Windows': '08',
            'Finishes': '09',
            'Drywall': '09',
            'Specialties': '10',
            'Equipment': '11',
            'Furnishings': '12',
            'Plumbing': '22',
            'HVAC': '23',
            'Electrical': '26',
            'Communications': '27',
            'Safety': '28',
            'Earthwork': '31',
            'Exterior': '32',
            'Utilities': '33'
        }
        return division_map.get(category, '')

    def _map_division_to_category(self, division: str) -> str:
        category_map = {
            '03': 'Concrete',
            '04': 'Masonry',
            '05': 'Steel',
            '06': 'Lumber',
            '07': 'Insulation',
            '08': 'Doors & Windows',
            '09': 'Finishes',
            '10': 'Specialties',
            '11': 'Equipment',
            '12': 'Furnishings',
            '22': 'Plumbing',
            '23': 'HVAC',
            '26': 'Electrical',
            '27': 'Communications',
            '28': 'Safety',
            '31': 'Earthwork',
            '32': 'Exterior',
            '33': 'Utilities'
        }
        div_code = division[:2] if division else ''
        return category_map.get(div_code, 'General')


provider_registry.register('rsmeans', RSMeansProviderAdapter)

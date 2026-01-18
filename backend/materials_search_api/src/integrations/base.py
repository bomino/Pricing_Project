from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
import httpx


@dataclass
class MaterialPrice:
    external_id: str
    name: str
    price: float
    unit: str
    currency: str = 'USD'
    confidence_score: float = 1.0
    source_url: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None


@dataclass
class SyncResult:
    success: bool
    items_processed: int
    items_failed: int
    error_message: Optional[str] = None
    prices: Optional[List[MaterialPrice]] = None


class DataProviderAdapter(ABC):
    def __init__(self, provider_config: Dict[str, Any]):
        self.name = provider_config.get('name', 'Unknown')
        self.base_url = provider_config.get('base_url', '')
        self.api_key = provider_config.get('api_key')
        self.config = provider_config.get('config', {})
        self.rate_limit_requests = provider_config.get('rate_limit_requests', 100)
        self.rate_limit_period = provider_config.get('rate_limit_period', 3600)
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                headers=self._get_headers()
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _get_headers(self) -> Dict[str, str]:
        headers = {'User-Agent': 'MaterialsSearch/1.0'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers

    @abstractmethod
    async def fetch_prices(
        self,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 100
    ) -> SyncResult:
        pass

    @abstractmethod
    async def fetch_single_price(self, external_id: str) -> Optional[MaterialPrice]:
        pass

    @abstractmethod
    async def search_materials(
        self,
        query: str,
        limit: int = 20
    ) -> List[MaterialPrice]:
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        pass

    def map_to_canonical_category(self, provider_category: str) -> Optional[str]:
        category_mapping = self.config.get('category_mapping', {})
        return category_mapping.get(provider_category)

    def calculate_confidence(self, raw_data: Dict[str, Any]) -> float:
        base_confidence = 0.8
        if raw_data.get('verified'):
            base_confidence += 0.1
        if raw_data.get('recent_update'):
            base_confidence += 0.1
        return min(base_confidence, 1.0)


class APIProviderAdapter(DataProviderAdapter):
    async def validate_connection(self) -> bool:
        try:
            client = await self.get_client()
            response = await client.get('/health')
            return response.status_code == 200
        except Exception:
            return False


class ScraperProviderAdapter(DataProviderAdapter):
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.respect_robots_txt = self.config.get('respect_robots_txt', True)
        self.delay_between_requests = self.config.get('delay_seconds', 2)

    async def validate_connection(self) -> bool:
        try:
            client = await self.get_client()
            response = await client.get('/')
            return response.status_code < 500
        except Exception:
            return False

    async def check_robots_txt(self) -> bool:
        if not self.respect_robots_txt:
            return True
        try:
            client = await self.get_client()
            response = await client.get('/robots.txt')
            return True
        except Exception:
            return True

import random
from typing import Optional, List
from .base import APIProviderAdapter, MaterialPrice, SyncResult
from .registry import provider_registry


class DemoProviderAdapter(APIProviderAdapter):
    async def fetch_prices(
        self,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 100
    ) -> SyncResult:
        demo_prices = self._generate_demo_data(category, limit)
        return SyncResult(
            success=True,
            items_processed=len(demo_prices),
            items_failed=0,
            prices=demo_prices
        )

    async def fetch_single_price(self, external_id: str) -> Optional[MaterialPrice]:
        return MaterialPrice(
            external_id=external_id,
            name=f"Demo Material {external_id}",
            price=round(random.uniform(50, 500), 2),
            unit="EA",
            confidence_score=0.9,
            source_url=f"{self.base_url}/materials/{external_id}"
        )

    async def search_materials(self, query: str, limit: int = 20) -> List[MaterialPrice]:
        return self._generate_demo_data(None, limit)

    async def validate_connection(self) -> bool:
        return True

    def _generate_demo_data(self, category: Optional[str], limit: int) -> List[MaterialPrice]:
        categories = ['Steel', 'Concrete', 'Lumber', 'Cement'] if not category else [category]
        prices = []
        for i in range(min(limit, 20)):
            cat = random.choice(categories)
            prices.append(MaterialPrice(
                external_id=f"DEMO-{i:04d}",
                name=f"Demo {cat} Product {i}",
                price=round(random.uniform(25, 750), 2),
                unit=random.choice(['EA', 'LF', 'SF', 'CY']),
                category=cat,
                confidence_score=round(random.uniform(0.7, 1.0), 2),
                source_url=f"{self.base_url}/materials/DEMO-{i:04d}"
            ))
        return prices


provider_registry.register('demo', DemoProviderAdapter)

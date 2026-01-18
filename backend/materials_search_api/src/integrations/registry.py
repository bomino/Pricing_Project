from typing import Dict, Type, Optional
from .base import DataProviderAdapter


class ProviderRegistry:
    def __init__(self):
        self._adapters: Dict[str, Type[DataProviderAdapter]] = {}

    def register(self, provider_name: str, adapter_class: Type[DataProviderAdapter]):
        self._adapters[provider_name.lower()] = adapter_class

    def get_adapter_class(self, provider_name: str) -> Optional[Type[DataProviderAdapter]]:
        return self._adapters.get(provider_name.lower())

    def list_providers(self) -> list:
        return list(self._adapters.keys())


provider_registry = ProviderRegistry()


def get_provider_adapter(provider_name: str, config: dict) -> Optional[DataProviderAdapter]:
    adapter_class = provider_registry.get_adapter_class(provider_name)
    if adapter_class:
        return adapter_class(config)
    return None

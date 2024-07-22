from typing import Any, Type, Callable
from abc import ABC, abstractmethod
from pydantic import BaseModel

from src.cache.serializers.base import BaseSerializer


class CacheManager(ABC):
    def __init__(self, serializer: BaseSerializer):
        self.serializer = serializer

    @abstractmethod
    async def get(self, key: str) -> Any:
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, expire: int) -> None:
        ...

    @abstractmethod
    def cache(self, model: Type[BaseModel], cache_key_prefix: str, expire: int) -> Callable:
        ...

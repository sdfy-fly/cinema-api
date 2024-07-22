from functools import wraps
from typing import Any, Type, Callable
from redis.asyncio import Redis
from pydantic import BaseModel

from src.cache.managers.base import CacheManager
from src.cache.serializers.base import BaseSerializer


class RedisCacheManager(CacheManager):
    def __init__(self, redis: Redis, serializer: BaseSerializer):
        super().__init__(serializer)
        self.redis = redis

    async def get(self, key: str) -> Any:
        return await self.redis.get(key)

    async def set(self, key: str, value: Any, expire: int) -> None:
        await self.redis.set(key, self.serializer.serialize(value), ex=expire)

    def cache(self, model: Type[BaseModel], cache_key_prefix: str, expire: int = 60 * 5) -> Callable:
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                request = kwargs.get('request')
                if request is None:
                    raise ValueError('Request object must be provided in kwargs')

                cache_key = f"{cache_key_prefix}:{request.url}"
                cached_data = await self.get(cache_key)
                if cached_data:
                    return self.serializer.deserialize(cached_data, model)

                response = await func(*args, **kwargs)
                await self.set(cache_key, response, expire)
                return response
            return wrapper
        return decorator

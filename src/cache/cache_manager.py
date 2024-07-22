from redis.asyncio import Redis

from src.cache.managers.redis import RedisCacheManager
from src.cache.serializers.json import JsonSerializer
from src.core.config import settings


def get_redis_cache_manager():
    redis = Redis(host=settings.redis.host, port=settings.redis.port)
    serializer = JsonSerializer()
    cache_manager = RedisCacheManager(redis=redis, serializer=serializer)
    return cache_manager

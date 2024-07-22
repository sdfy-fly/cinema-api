import pytest
from redis.asyncio import Redis

from tests.functional.settings import test_settings


@pytest.fixture(name='redis_client', scope='session')
async def redis_client():
    """ Асинхронная фикстура для создания клиента Redis. """
    client = Redis(host=test_settings.redis.host, port=test_settings.redis.port)
    yield client
    await client.aclose()

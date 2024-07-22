import asyncio

import pytest

# Импортируем фикстуры из модулей
pytest_plugins = [
    'tests.functional.fixtures.elastic',
    'tests.functional.fixtures.http',
    'tests.functional.fixtures.redis',
]


@pytest.fixture(scope='session', autouse=True)
def event_loop():
    """ Создает и предоставляет asyncio event loop для всех тестов в сессии. """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

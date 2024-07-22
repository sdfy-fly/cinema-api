import pytest
from httpx import AsyncClient, Response


@pytest.fixture(name='make_get_request')
def make_get_request():
    """
    Фикстура для выполнения HTTP GET-запросов с помощью AsyncClient.
    Принимает URL и параметры запроса, возвращает HTTP-ответ.
    """

    async def inner(url: str, query_data: dict = None) -> Response:
        async with AsyncClient() as client:
            return await client.get(url, params=query_data)

    return inner

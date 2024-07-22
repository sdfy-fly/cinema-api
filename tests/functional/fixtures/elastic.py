import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from tests.functional.settings import test_settings


@pytest.fixture(name='es_client', scope='session')
async def es_client():
    """ Асинхронная фикстура для создания клиента Elasticsearch. """
    es_client = AsyncElasticsearch(hosts=test_settings.elastic.url, verify_certs=False)
    yield es_client
    await es_client.close()


@pytest.fixture(name='es_write_data')
def es_write_data(es_client):
    """
    Фикстура для записи данных в Elasticsearch.
    Предоставляет функцию, которая инициализирует индекс, загружает данные и обновляет индекс.
    """

    async def inner(index_name: str, index_schema: dict, data: list[dict]):
        if await es_client.indices.exists(index=index_name):
            await es_client.indices.delete(index=index_name)

        await es_client.indices.create(index=index_name, **index_schema)
        updated, errors = await async_bulk(client=es_client, actions=data)
        await es_client.indices.refresh(index=index_name)

        await es_client.close()
        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner

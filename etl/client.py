import logging

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

logger = logging.getLogger(__name__)


class ElasticLoader:
    """ Класс для добавления данных в Elastic """

    def __init__(self, es: AsyncElasticsearch, batch_size: int = 100):
        self._es = es
        self.batch_size = batch_size

    async def create_index(self, name: str, schema: dict):
        """ Функция создания индекса, если его еще не было """

        if await self._es.indices.exists(index=name):
            logger.info(f'Индекс {name} уже существует')
            return None

        await self._es.indices.create(index=name, body=schema)
        logger.info(f'Создан индекс {name}')

    async def load_data(self, index_name: str, data: list[dict]):
        """ Загружает данные в Elasticsearch пачками """

        actions = self.generate_actions(index_name, data)
        success, failed = await async_bulk(self._es, actions)

        logger.info(f'Записал {success} строк в индекс {index_name}')

    @staticmethod
    def generate_actions(index_name: str, items: list[dict]):
        for item in items:
            yield {
                '_op_type': 'index',
                '_index': index_name,
                '_id': item['id'],
                '_source': item,
            }

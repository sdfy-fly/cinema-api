import asyncio
import json
import os

from elasticsearch import AsyncElasticsearch

from etl.client import ElasticLoader
from src.core.config import settings

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

ENTITY_MAPPER = {
    'movies': {
        'dump': os.path.join(CURRENT_DIR, 'dumps', 'movies_dump.json'),
        'schema': os.path.join(CURRENT_DIR, 'schemas', 'movies_index_schema.json'),
    },
    'persons': {
        'dump': os.path.join(CURRENT_DIR, 'dumps', 'persons_dump.json'),
        'schema': os.path.join(CURRENT_DIR, 'schemas', 'persons_index_schema.json'),
    },
    'genres': {
        'dump': os.path.join(CURRENT_DIR, 'dumps', 'genres_dump.json'),
        'schema': os.path.join(CURRENT_DIR, 'schemas', 'genres_index_schema.json'),
    },
}


def get_file_data(filepath: str):
    with open(filepath, 'r', encoding='UTF-8') as file:
        return json.load(file)


async def process_data(loader: ElasticLoader, index_name: str, schema: dict, items: list[dict]):
    await loader.create_index(index_name, schema)
    await loader.load_data(index_name, items)


async def main():
    client = AsyncElasticsearch(hosts=[settings.elastic.url])

    for index_name, entity in ENTITY_MAPPER.items():
        items: list[dict] = get_file_data(entity['dump'])
        schema: dict = get_file_data(entity['schema'])
        try:
            loader = ElasticLoader(client)
            await process_data(loader, index_name, schema, items)
        finally:
            await client.close()


if __name__ == '__main__':
    asyncio.run(main())

import json
import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class ElasticSearchTestSettings(BaseSettings):
    host: str = Field(alias='ELASTIC_HOST', default='127.0.0.1')
    port: int = Field(alias='ELASTIC_PORT', default=9200)

    @property
    def url(self) -> str:
        return f'http://{self.host}:{self.port}'

    @property
    def movie_index(self):
        index_name = 'movies'
        index_schema = self._load_schema('etl/schemas/movies_index_schema.json')
        return index_name, index_schema

    @property
    def genre_index(self):
        index_name = 'genres'
        index_schema = self._load_schema('etl/schemas/genres_index_schema.json')
        return index_name, index_schema

    @property
    def person_index(self):
        index_name = 'persons'
        index_schema = self._load_schema('etl/schemas/persons_index_schema.json')
        return index_name, index_schema

    @staticmethod
    def _load_schema(path: str):
        with open(TestSettings().base_dir / path, 'r', encoding='UTF-8') as file:
            return json.load(file)


class RedisTestSettings(BaseSettings):
    host: str = Field(alias='REDIS_HOST', default='127.0.0.1')
    port: int = Field(alias='REDIS_PORT', default=6379)


class ServiceTestSettings(BaseSettings):
    host: str = Field(alias='SERVICE_HOST', default='127.0.0.1')
    port: int = Field(alias='SERVICE_PORT', default=8001)

    @property
    def url(self):
        return f'http://{self.host}:{self.port}'


class TestSettings(BaseSettings):
    elastic: ElasticSearchTestSettings = ElasticSearchTestSettings()
    redis: RedisTestSettings = RedisTestSettings()
    service: ServiceTestSettings = ServiceTestSettings()
    base_dir: Path = Path(os.path.dirname(__file__)).parent.parent.resolve()


test_settings = TestSettings()

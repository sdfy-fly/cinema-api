from logging import config as logging_config

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

from src.core.logger import LOGGING

load_dotenv()

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class RedisSettings(BaseSettings):
    host: str = Field(alias='REDIS_HOST', default='127.0.0.1')
    port: int = Field(alias='REDIS_PORT', default=6379)


class ElasticSettings(BaseSettings):
    host: str = Field(alias='ELASTIC_HOST', default='127.0.0.1')
    port: int = Field(alias='ELASTIC_PORT', default=9200)
    protocol: str = Field(alias='ELASTIC_SCHEMA', default='http')

    @property
    def url(self) -> str:
        return f'{self.protocol}://{self.host}:{self.port}'


class Settings(BaseSettings):
    project_name: str = Field(alias='PROJECT_NAME', default='movies')
    redis: RedisSettings = RedisSettings()
    elastic: ElasticSettings = ElasticSettings()


settings = Settings()

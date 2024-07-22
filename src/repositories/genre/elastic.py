from typing import Any

from elasticsearch import NotFoundError, AsyncElasticsearch

from src.constants.elastic import ElasticIndexNames
from src.models.base import BasePaginationParams
from src.repositories.genre.base import BaseGenreRepository


class ElasticGenreRepository(BaseGenreRepository):

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def all(self, params: BasePaginationParams) -> list[dict[str, Any]]:
        """ Получает все жанры из эластика с пагинацией """
        body = {
            'size': params.limit,
            'from': params.offset,
        }

        try:
            response = await self.elastic.search(
                index=ElasticIndexNames.GENRE.value,
                body=body,
            )
        except NotFoundError:
            return []

        return response['hits']['hits']

    async def get_by_id(self, genre_id: str) -> dict[str, Any] | None:
        """ Получает жанр из эластика по id """
        try:
            return await self.elastic.get(
                index=ElasticIndexNames.GENRE.value,
                id=genre_id,
            )
        except NotFoundError:
            return None

    async def get_films(self, genre_id: str, params: BasePaginationParams) -> list[dict[str, Any]]:
        """ Получение фильмов с пагинацией по жанру """
        query = {
            'nested': {
                'path': 'genres',
                'query': {'bool': {'must': [{'match': {'genres.id': genre_id}}]}},
            },
        }

        body = {
            'size': params.limit,
            'from': params.offset,
            'query': query,
        }

        try:
            response = await self.elastic.search(
                index=ElasticIndexNames.MOVIE.value,
                body=body,
            )
        except NotFoundError:
            return []

        return response['hits']['hits']

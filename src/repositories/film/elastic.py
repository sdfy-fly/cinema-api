from typing import Any

from elasticsearch import NotFoundError, AsyncElasticsearch

from src.constants.elastic import ElasticIndexNames
from src.models.film import FilmQueryParams, FilmSearchParams
from src.repositories.film.base import BaseFilmRepository


class ElasticFilmRepository(BaseFilmRepository):

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def all(self, params: FilmQueryParams) -> list[dict[str, Any]]:
        """ Достает фильмы из эластика по query параметрам """
        body = self._build_list_query_body(params)

        try:
            response = await self.elastic.search(
                index=ElasticIndexNames.MOVIE.value,
                body=body,
            )
        except NotFoundError as e:
            print(e)
            return []

        return response['hits']['hits']

    async def search(self, params: FilmSearchParams) -> list[dict[str, Any]]:
        """ Ищет фильмы по параметру query """
        body = self._build_search_query_body(params)

        try:
            response = await self.elastic.search(
                index=ElasticIndexNames.MOVIE.value,
                body=body,
            )
        except NotFoundError as e:
            print(e)
            return []

        return response['hits']['hits']

    async def get_by_id(self, film_id: str) -> dict[str, Any] | None:
        """ Получает фильм из эластика по id """
        try:
            return await self.elastic.get(
                index=ElasticIndexNames.MOVIE.value,
                id=film_id,
            )
        except NotFoundError:
            return None

    def _build_list_query_body(self, params: FilmQueryParams) -> dict[str, Any]:
        body = {
            'size': params.limit,
            'from': params.offset,
        }

        if query_body := self._build_list_query(params):
            body['query'] = query_body

        if sort := params.sort:
            body['sort'] = [{sort.field.value: {'order': sort.order.value}}]

        return body

    def _build_search_query_body(self, params: FilmSearchParams) -> dict[str, Any]:
        body = {
            'size': params.limit,
            'from': params.offset,
        }

        if query_body := self._build_search_query(params):
            body['query'] = query_body

        return body

    @staticmethod
    def _build_search_query(params: FilmSearchParams) -> dict[str, Any]:
        must_clauses = []

        if search := params.query:
            must_clauses.append({
                'multi_match': {
                    'query': search,
                    'fuzziness': 'AUTO',
                },
            })

        return {'bool': {'must': must_clauses}} if must_clauses else {}

    @staticmethod
    def _build_list_query(params: FilmQueryParams) -> dict[str, Any]:
        must_clauses = []

        if genre := params.genre:
            must_clauses.append({
                'nested': {
                    'path': 'genres',
                    'query': {
                        'term': {'genres.id': genre},
                    },
                },
            })

        return {'bool': {'must': must_clauses}} if must_clauses else {}

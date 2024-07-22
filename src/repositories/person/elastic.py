from typing import Any

from elasticsearch import NotFoundError, AsyncElasticsearch

from src.constants.elastic import ElasticIndexNames
from src.models.base import BasePaginationParams
from src.models.person import PersonSearchParams
from src.repositories.person.base import BasePersonRepository


class ElasticPersonRepository(BasePersonRepository):

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def all(self, params: BasePaginationParams) -> list[dict[str, Any]]:
        """ Получает всех персон из эластика с пагинацией и поиском """
        body = {
            'size': params.limit,
            'from': params.offset,
        }

        try:
            response = await self.elastic.search(
                index=ElasticIndexNames.PERSON.value,
                body=body,
            )
        except NotFoundError:
            return []

        return response['hits']['hits']

    async def search(self, params: PersonSearchParams) -> list[dict[str, Any]]:
        """ Получает всех персон из эластика с пагинацией и поиском """
        body = {
            'size': params.limit,
            'from': params.offset,
        }

        if search := params.query:
            body['query'] = self._build_search_query_body(search)

        try:
            response = await self.elastic.search(
                index=ElasticIndexNames.PERSON.value,
                body=body,
            )
        except NotFoundError:
            return []

        return response['hits']['hits']

    async def get_by_id(self, person_id: str) -> dict[str, Any] | None:
        """ Получает персону из эластика по id """
        try:
            return await self.elastic.get(
                index=ElasticIndexNames.PERSON.value,
                id=person_id,
            )
        except NotFoundError:
            return None

    async def get_films(self, person_id: str, params: BasePaginationParams) -> list[dict[str, Any]]:
        """ Получение фильмов по персоне с пагинацией """
        query = {
            'bool': {
                'should': self._build_person_role_search_query(person_id),
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

    @staticmethod
    def _build_search_query_body(search: str):
        return {
            'bool': {
                'must': [{
                    'multi_match': {
                        'query': search,
                        'fuzziness': 'AUTO',
                    },
                }],
            },
        }

    @staticmethod
    def _build_person_role_search_query(person_id: str):
        return [
            {
                'nested': {
                    'path': role,
                    'query': {'match': {f"{role}.id": person_id}},
                },
            }
            for role in ['actors', 'directors', 'writers']
        ]

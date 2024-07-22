from functools import lru_cache
from typing import Annotated

from elasticsearch import AsyncElasticsearch
from fastapi import Depends, Query

from src.db.elastic import get_elastic
from src.dependencies.base import get_pagination_params
from src.models.base import BasePaginationParams
from src.models.person import PersonSearchParams
from src.repositories.person.elastic import ElasticPersonRepository
from src.serializers.person.elastic import ElasticPersonSerializer
from src.services.person import PersonService


def get_person_search_params(
        pagination: Annotated[BasePaginationParams, Depends(get_pagination_params)],
        query: str | None = Query(None, description='Строка поиска'),
) -> PersonSearchParams:
    """ Получает query параметры фильтрации и поиска для персон """

    return PersonSearchParams(
        limit=pagination.limit,
        offset=pagination.offset,
        query=query,
    )


@lru_cache()
def get_person_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    repository = ElasticPersonRepository(elastic)
    serializer = ElasticPersonSerializer()
    return PersonService(repository, serializer)

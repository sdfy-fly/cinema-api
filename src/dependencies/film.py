from functools import lru_cache
from typing import Annotated

from elasticsearch import AsyncElasticsearch
from fastapi import Depends, Query

from src.db.elastic import get_elastic
from src.dependencies.base import get_pagination_params
from src.models.base import BasePaginationParams
from src.models.film import FilmSearchParams, FilmQueryParams, FilmSortParams
from src.repositories.film.elastic import ElasticFilmRepository
from src.serializers.films.elastic import ElasticFilmSerializer
from src.services.film import FilmService


def get_film_list_params(
        pagination: Annotated[BasePaginationParams, Depends(get_pagination_params)],
        sort: str | None = Query('-imdb_rating', description='Параметр сортировки по рейтингу imdb'),
        genre: str | None = Query(None, description='Параметр фильтрации по id жанра'),
) -> FilmQueryParams:
    """ Получает query параметры сортировки фильтрации для фильмов """

    sorting = FilmSortParams.parse_sort_param(sort) if sort else None
    return FilmQueryParams(
        limit=pagination.limit,
        offset=pagination.offset,
        sort=sorting,
        genre=genre,
    )


def get_film_search_params(
        pagination: Annotated[BasePaginationParams, Depends(get_pagination_params)],
        query: str | None = Query(None, description='Строка поиска по названию фильма'),
) -> FilmSearchParams:
    """ Получает query параметры поиска для фильмов """

    return FilmSearchParams(
        limit=pagination.limit,
        offset=pagination.offset,
        query=query,
    )


@lru_cache()
def get_film_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    repository = ElasticFilmRepository(elastic)
    serializer = ElasticFilmSerializer()
    return FilmService(repository=repository, serializer=serializer)

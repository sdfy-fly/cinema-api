from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from src.db.elastic import get_elastic
from src.repositories.genre.elastic import ElasticGenreRepository
from src.serializers.genre.elastic import ElasticGenreSerializer
from src.services.genre import GenreService


@lru_cache()
def get_genre_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    repository = ElasticGenreRepository(elastic)
    serializer = ElasticGenreSerializer()
    return GenreService(repository, serializer)

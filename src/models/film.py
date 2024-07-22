from typing import Type
from uuid import UUID

from pydantic import BaseModel

from src.models.base import BaseSortField, BaseSortParams, BasePaginationParams


class Person(BaseModel):
    id: UUID
    name: str


class Genre(BaseModel):
    id: UUID
    name: str


class Film(BaseModel):
    id: UUID
    title: str
    description: str
    imdb_rating: float
    genres: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]

    class Config:
        from_attributes = True


class FilmSortField(BaseSortField):
    """ Enum полей доступных для сортировки фильмов """
    IMDB_RATING = 'imdb_rating'


class FilmSortParams(BaseSortParams):
    """ Класс для определения поля и порядка сортировки фильма """

    @classmethod
    def get_fields_class(cls) -> Type[FilmSortField]:
        return FilmSortField


class FilmQueryParams(BasePaginationParams):
    sort: FilmSortParams | None
    genre: str | None

    class Config:
        arbitrary_types_allowed = True


class FilmSearchParams(BasePaginationParams):
    query: str | None

    class Config:
        arbitrary_types_allowed = True

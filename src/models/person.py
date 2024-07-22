from uuid import UUID

from pydantic import BaseModel

from src.models.base import BasePaginationParams


class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: float


class Person(BaseModel):
    id: UUID
    name: str


class PersonSearchParams(BasePaginationParams):
    query: str | None

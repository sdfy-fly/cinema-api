from uuid import UUID

from pydantic import BaseModel


class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: float


class Genre(BaseModel):
    id: UUID
    name: str

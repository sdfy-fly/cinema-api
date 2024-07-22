from abc import ABC, abstractmethod
from typing import Any

from src.models.film import FilmQueryParams, FilmSearchParams


class BaseFilmRepository(ABC):

    @abstractmethod
    async def all(self, params: FilmQueryParams) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def search(self, params: FilmSearchParams) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_by_id(self, film_id: str) -> dict[str, Any] | None:
        ...

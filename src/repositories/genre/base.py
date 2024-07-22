from abc import ABC, abstractmethod
from typing import Any

from src.models.base import BasePaginationParams


class BaseGenreRepository(ABC):

    @abstractmethod
    async def all(self, params: BasePaginationParams) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_by_id(self, genre_id: str) -> dict[str, Any] | None:
        ...

    @abstractmethod
    async def get_films(self, genre_id: str, params: BasePaginationParams) -> list[dict[str, Any]]:
        ...

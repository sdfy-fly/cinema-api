from abc import ABC, abstractmethod
from typing import Any

from src.models.base import BasePaginationParams
from src.models.person import PersonSearchParams


class BasePersonRepository(ABC):

    @abstractmethod
    async def all(self, params: BasePaginationParams) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def search(self, params: PersonSearchParams) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_by_id(self, person_id: str) -> dict[str, Any] | None:
        ...

    @abstractmethod
    async def get_films(self, person_id: str, params: BasePaginationParams) -> list[dict[str, Any]]:
        ...

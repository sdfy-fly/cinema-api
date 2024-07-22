from abc import ABC, abstractmethod

from src.models.film import Film


class BaseFilmSerializer(ABC):

    @abstractmethod
    def serialize(self, film: dict) -> Film:
        ...

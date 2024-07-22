from abc import ABC, abstractmethod

from src.models.person import Person, Film


class BasePersonSerializer(ABC):

    @abstractmethod
    def serialize(self, data: dict) -> Person:
        ...

    @abstractmethod
    def serialize_movie(self, data: dict) -> Film:
        ...

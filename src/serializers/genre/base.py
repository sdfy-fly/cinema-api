from abc import ABC, abstractmethod

from src.models.genre import Film, Genre


class BaseGenreSerializer(ABC):

    @abstractmethod
    def serialize(self, genre: dict) -> Genre:
        ...

    @abstractmethod
    def serialize_movie(self, data: dict) -> Film:
        ...

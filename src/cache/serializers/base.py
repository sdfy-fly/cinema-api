from typing import Any, Type
from abc import ABC, abstractmethod
from pydantic import BaseModel


class BaseSerializer(ABC):
    @abstractmethod
    def serialize(self, data: Any) -> str:
        ...

    @abstractmethod
    def deserialize(self, data: str, model: Type[BaseModel]) -> Any:
        ...

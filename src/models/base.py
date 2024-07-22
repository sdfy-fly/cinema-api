from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Type

from fastapi import HTTPException, Query
from pydantic import BaseModel, Field


class SortOrder(str, Enum):
    ASC = 'asc'
    DESC = 'desc'


class BaseSortField(Enum):
    @classmethod
    def get_values(cls):
        return [e.value for e in cls]


@dataclass
class BaseSortParams(ABC):
    """ Базовый класс параметров сортировки """
    field: BaseSortField
    order: SortOrder

    @classmethod
    def parse_sort_param(cls, sort: str):
        order = SortOrder.ASC
        if sort.startswith('-'):
            order = SortOrder.DESC
            sort = sort[1:]

        fields_class = cls.get_fields_class()
        if sort not in fields_class.get_values():
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort}")

        field = fields_class(sort)
        return cls(field=field, order=order)

    @classmethod
    @abstractmethod
    def get_fields_class(cls) -> Type[BaseSortField]:
        ...

    def __repr__(self):
        return f'{self.field.value}, {self.order.value}'


class BasePaginationParams(BaseModel):
    """ Базовый класс параметров пагинации """
    limit: int = Field(
        Query(alias='page_size', gt=0),
    )
    offset: int = Field(
        Query(alias='page_number', ge=0),
    )

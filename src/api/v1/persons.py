from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Request, Path

from src.dependencies.base import get_pagination_params
from src.dependencies.person import get_person_service, get_person_search_params
from src.exceptions.person import PersonNotFound
from src.models.base import BasePaginationParams
from src.models.person import PersonSearchParams, Person, Film
from src.services.person import PersonService
from src.cache.cache_manager import get_redis_cache_manager

router = APIRouter()
cache_manager = get_redis_cache_manager()


@router.get(
    '',
    summary='Список персон',
    response_model=List[Person],
)
@cache_manager.cache(Person, 'person_all')
async def person_list(
        request: Request,
        person_service: Annotated[PersonService, Depends(get_person_service)],
        params: Annotated[BasePaginationParams, Depends(get_pagination_params)],
) -> List[Person]:
    """
    Получает список персон
    \f
    :param request: объект запроса FastAPI.
    :param person_service: сервис для работы с базой персон.
    :param params: query-параметры для вывода результата (page_size, page_number).
    :return: список объектов типа Genre.
    """

    return await person_service.all(params)


@router.get(
    '/search',
    summary='Поиск персон',
    response_model=List[Person],
)
@cache_manager.cache(Person, 'person_search')
async def person_search(
        request: Request,
        person_service: Annotated[PersonService, Depends(get_person_service)],
        params: Annotated[PersonSearchParams, Depends(get_person_search_params)],
) -> List[Person]:
    """
    Получает список персон на основе параметра поиска по ФИО
    \f
    :param request: объект запроса FastAPI.
    :param person_service: сервис для работы с базой персон.
    :param params: query-параметры для поиска персон и вывода результата (query, page_size, page_number).
    :return: список объектов типа Person.
    """

    return await person_service.search(params)


@router.get(
    '/{person_id}',
    response_model=Person,
    summary='Данные о персоне',
)
@cache_manager.cache(Person, 'person')
async def person_details(
        request: Request,
        person_service: Annotated[PersonService, Depends(get_person_service)],
        person_id: str = Path(..., description='uuid персоны'),
) -> Person:
    """
    Получает информацию о персоне по её ID:
    - **id**: uuid персоны
    - **name**: ФИО персоны
    \f
    :param request: объект запроса FastAPI.
    :param person_service: сервис для работы с базой персон.
    :param person_id: path-параметр идентификатора персоны.
    :return: объект типа Person.
    """

    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Person not found')

    return person


@router.get(
    '/{person_id}/films',
    response_model=List[Film],
    summary='Фильмы по персоне',
)
@cache_manager.cache(Film, 'films_by_person')
async def person_films(
        request: Request,
        person_service: Annotated[PersonService, Depends(get_person_service)],
        params: Annotated[BasePaginationParams, Depends(get_pagination_params)],
        person_id: str = Path(..., description='uuid персоны'),
) -> List[Film]:
    """
    Получает список фильмов персоны по её id
    \f
    :param request: объект запроса FastAPI.
    :param person_service: сервис для работы с базой персон.
    :param person_id: path-параметр идентификатора персоны.
    :return: список объектов типа Film.
    """

    try:
        films = await person_service.get_films_by_person(person_id, params)
    except PersonNotFound as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=e.message)

    return films

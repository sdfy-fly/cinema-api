from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Request, Path

from src.dependencies.film import get_film_service, get_film_list_params, get_film_search_params
from src.models.film import Film, FilmQueryParams
from src.services.film import FilmService
from src.cache.cache_manager import get_redis_cache_manager

router = APIRouter()
cache_manager = get_redis_cache_manager()


@router.get(
    '',
    summary='Список фильмов',
)
@cache_manager.cache(Film, 'films_all')
async def film_list(
        request: Request,
        film_service: Annotated[FilmService, Depends(get_film_service)],
        params: Annotated[FilmQueryParams, Depends(get_film_list_params)],
) -> List[Film]:
    """
    Получает список фильмов по параметрам фильтрации (по id жанра) и сортировки (по рейтингу imdb)
    \f
    :param request: объект запроса FastAPI.
    :param film_service: сервис для работы с базой фильмов.
    :param params: query-параметры для фильтрации и сортировки фильмов и вывода результата (sort, genre, page_size, page_number).
    :return: список объектов типа Film.
    """

    return await film_service.all(params)


@router.get(
    '/search',
    summary='Поиск по фильмам',
)
@cache_manager.cache(Film, 'films_search')
async def film_search(
        request: Request,
        film_service: Annotated[FilmService, Depends(get_film_service)],
        params: Annotated[FilmQueryParams, Depends(get_film_search_params)],
) -> List[Film]:
    """
    Получает список фильмов на основе параметра поиска по названию
    \f
    :param request: объект запроса FastAPI.
    :param film_service: сервис для работы с базой фильмов.
    :param params: query-параметры для поиска фильмов и вывода результата (query, page_size, page_number).
    :return: список объектов типа Film.
    """
    return await film_service.search(params)


@router.get(
    '/{film_id}',
    response_model=Film,
    summary='Данные по фильму',
)
@cache_manager.cache(Film, 'film')
async def film_details(
        request: Request,
        film_service: Annotated[FilmService, Depends(get_film_service)],
        film_id: str = Path(..., description='uuid фильма'),
) -> Film:
    """
    Получает информацию о фильме по id:
    - **id**: uuid фильма
    - **title**: название фильма
    - **description**: описание фильма
    - **imdb_rating**: рейтинг по данным imdb
    - **genres**: список жанров
    - **actors**: список актёров
    - **writers**: список сценаристов
    - **directors**: список список режиссёров
    \f
    :param request: объект запроса FastAPI.
    :param film_service: сервис для работы с базой фильмов.
    :param film_id: path-параметр идентификатора фильма.
    :return: объект типа Film.
    """

    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Film not found')

    return film

from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Request, Path

from src.dependencies.base import get_pagination_params
from src.dependencies.genre import get_genre_service
from src.exceptions.genre import GenreNotFound
from src.models.base import BasePaginationParams
from src.models.genre import Genre, Film
from src.services.genre import GenreService
from src.cache.cache_manager import get_redis_cache_manager

router = APIRouter()
cache_manager = get_redis_cache_manager()


@router.get(
    '',
    summary='Список жанров',
    response_model=List[Genre],
)
@cache_manager.cache(Genre, 'genres_all')
async def genre_list(
        request: Request,
        genre_service: Annotated[GenreService, Depends(get_genre_service)],
        params: Annotated[BasePaginationParams, Depends(get_pagination_params)],
) -> List[Genre]:
    """
    Получает список жанров
    \f
    :param request: объект запроса FastAPI.
    :param genre_service: сервис для работы с базой жанров.
    :param params: query-параметры для вывода результата (page_size, page_number).
    :return: список объектов типа Genre.
    """

    return await genre_service.all(params)


@router.get(
    '/{genre_id}',
    response_model=Genre,
    summary='Данные по жанру',
)
@cache_manager.cache(Genre, 'genre')
async def genre_details(
        request: Request,
        genre_service: Annotated[GenreService, Depends(get_genre_service)],
        genre_id: str = Path(..., description='uuid персоны'),
) -> Genre:
    """
    Получает информацию о жанре по его id:
    - **id**: uuid жанра
    - **name**: название жанра
    \f
    :param request: объект запроса FastAPI.
    :param genre_service: сервис для работы с базой жанров.
    :param genre_id: path-параметр идентификатора жанра.
    :return: объект типа Genre.
    """

    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genre not found')

    return genre


@router.get(
    '/{genre_id}/films',
    response_model=List[Film],
    summary='Популярные фильмы в жанре',
)
@cache_manager.cache(Film, 'films_by_genre')
async def genre_films(
        request: Request,
        genre_service: Annotated[GenreService, Depends(get_genre_service)],
        params: Annotated[BasePaginationParams, Depends(get_pagination_params)],
        genre_id: str = Path(..., description='uuid персоны'),
) -> List[Film]:
    """
    Получает список фильмов по id жанра с наивысшим рейтингом imdb
    \f
    :param request: объект запроса FastAPI.
    :param genre_service: сервис для работы с базой жанров.
    :param genre_id: path-параметр идентификатора жанра.
    :param params: query-параметры для вывода результата (page_size, page_number).
    :return: список объектов типа Film.
    """

    try:
        films = await genre_service.get_films_by_genre(genre_id, params)
    except GenreNotFound as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=e.message)

    return films

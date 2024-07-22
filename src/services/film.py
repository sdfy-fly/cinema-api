from src.models.film import Film, FilmQueryParams, FilmSearchParams
from src.repositories.film.base import BaseFilmRepository
from src.serializers.films.base import BaseFilmSerializer


class FilmService:
    def __init__(self, repository: BaseFilmRepository, serializer: BaseFilmSerializer):
        self.repo = repository
        self.serializer = serializer

    async def all(self, params: FilmQueryParams) -> list[Film]:
        """ Возвращает список фильмов """

        if films := await self.repo.all(params):
            return [self.serializer.serialize(film) for film in films]

        return []

    async def search(self, params: FilmSearchParams) -> list[Film]:
        """ Возвращает список фильмов """

        if films := await self.repo.search(params):
            return [self.serializer.serialize(film) for film in films]

        return []

    async def get_by_id(self, film_id: str) -> Film | None:
        """ Возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе """

        if film := await self.repo.get_by_id(film_id):
            return self.serializer.serialize(film)

        return None

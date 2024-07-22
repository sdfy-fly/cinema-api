from src.exceptions.genre import GenreNotFound
from src.models.base import BasePaginationParams
from src.models.genre import Film, Genre
from src.repositories.genre.base import BaseGenreRepository
from src.serializers.genre.base import BaseGenreSerializer


class GenreService:
    def __init__(self, repository: BaseGenreRepository, serializer: BaseGenreSerializer):
        self.repo = repository
        self.serializer = serializer

    async def all(self, params: BasePaginationParams) -> list[Genre]:
        """ Получение всех жанров с пагинацией """

        if genres := await self.repo.all(params):
            return [self.serializer.serialize(genre) for genre in genres]

        return []

    async def get_by_id(self, genre_id: str) -> Genre | None:
        """ Получение жанра по Id """
        if genre := await self.repo.get_by_id(genre_id):
            return self.serializer.serialize(genre)

        return None

    async def get_films_by_genre(self, genre_id: str, params: BasePaginationParams) -> list[Film]:
        """ Получение списка фильмов по id жанра """

        if not await self.repo.get_by_id(genre_id):
            raise GenreNotFound('Жанр не найден!')

        if films := await self.repo.get_films(genre_id, params):
            return [self.serializer.serialize_movie(film) for film in films]

        return []

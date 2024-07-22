from src.exceptions.person import PersonNotFound
from src.models.base import BasePaginationParams
from src.models.person import Film, Person, PersonSearchParams

from src.repositories.person.base import BasePersonRepository
from src.serializers.person.base import BasePersonSerializer


class PersonService:
    def __init__(self, repository: BasePersonRepository, serializer: BasePersonSerializer):
        self.repo = repository
        self.serializer = serializer

    async def all(self, params: BasePaginationParams) -> list[Person]:
        """ Получение всех персон с пагинацией """

        if persons := await self.repo.all(params):
            return [self.serializer.serialize(person) for person in persons]

        return []

    async def search(self, params: PersonSearchParams) -> list[Person]:
        """ Получение персон с пагинацией по поиску """

        if persons := await self.repo.search(params):
            return [self.serializer.serialize(person) for person in persons]

        return []

    async def get_by_id(self, person_id: str) -> Person | None:
        """ Получение персоны по Id """

        if person := await self.repo.get_by_id(person_id):
            return self.serializer.serialize(person)

        return None

    async def get_films_by_person(self, person_id: str, params: BasePaginationParams) -> list[Film]:
        """ Получение списка фильмов по id персоны """

        if not await self.repo.get_by_id(person_id):
            raise PersonNotFound('Персона не найдена!')

        if films := await self.repo.get_films(person_id, params):
            return [self.serializer.serialize_movie(film) for film in films]

        return []

import uuid
import json
import random
from faker import Faker
from abc import ABC, abstractmethod
from typing import List, Dict, Any

fake = Faker()

GENRES = [
    'Sci-Fi', 'Action', 'Romance', 'Animation', 'Adventure', 'Fantasy', 'Drama', 'Documentary',
    'Comedy', 'Short', 'Reality-TV', 'History', 'Family', 'Musical', 'War', 'Mystery', 'Music',
    'Thriller', 'Biography', 'Crime', 'Western', 'News', 'Game-Show', 'Horror', 'Talk-Show', 'Sport',
]


class DataGenerator(ABC):
    """
    Абстрактный базовый класс для всех генераторов данных.
    Определяет методы для получения загруженных и генерированных данных.
    """
    @abstractmethod
    async def get_generated_data(self, count: int) -> List[Dict[str, Any]]:
        """Генерирует заданное количество данных. Должен быть реализован в производных классах."""
        ...

    async def get_loaded_data(self, path: str) -> List[Dict[str, Any]]:
        """Загружает данные из JSON файла по указанному пути."""
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    async def get_test_data(self, path: str, count: int = 1):
        """Возвращает смешанные загруженные и генерированные данные."""
        loaded_data = await self.get_loaded_data(path)
        generated_data = await self.get_generated_data(count)
        return random.shuffle(loaded_data + generated_data)


class FilmGenerator(DataGenerator):
    """ Генератор данных для фильмов, создает список фильмов со случайными данными. """
    async def get_generated_data(self, title: str = '', count: int = 1) -> List[Dict[str, Any]]:
        films = []
        for _ in range(count):
            genres = [
                {'id': '6c162475-c7ed-4461-9184-001ef3d9f26e', 'name': 'Sci-Fi'},
                {'id': '3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff', 'name': 'Action'},
            ]
            directors = [
                {'id': '8cab6731-8fc6-4519-a9dc-c999610014fa', 'name': 'John'},
            ]
            writers = [
                {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
                {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'},
            ]
            actors = [
                {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
                {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'},
            ]
            films.append({
                'id': str(uuid.uuid4()),
                'imdb_rating': round(random.uniform(0, 10), 1),
                'genres': genres,
                'title':  title if title else fake.catch_phrase(),
                'description': fake.text(),
                'directors_names': [director['name'] for director in directors],
                'actors_names': [actor['name'] for actor in actors],
                'writers_names': [writer['name'] for writer in writers],
                'actors': actors,
                'writers': writers,
                'directors': directors,
            })
        return films


class PersonGenerator(DataGenerator):
    """ Генератор данных для персон, создает список персон с случайными именами. """
    async def get_generated_data(self, name: str = '', count: int = 1) -> List[Dict[str, Any]]:
        persons = [
            {
                'id': str(uuid.uuid4()),
                'name': name if name else fake.name(),
            } for _ in range(count)
        ]
        return persons


class GenreGenerator(DataGenerator):
    """ Генератор данных для жанров, создает список жанров из предопределенного списка GENRES. """
    async def get_generated_data(self, count: int = 1) -> List[Dict[str, Any]]:
        genres = [{'id': str(uuid.uuid4()), 'name': genre} for genre in random.sample(GENRES, count)]
        return genres


async def generate_bulk_query(data_generator: list, index_name: str):
    """
    Создает и возвращает массовый запрос Elasticsearch для передачи данных.
    В каждую запись добавляется индекс и уникальный идентификатор.
    """
    bulk_query: list[dict] = []
    for row in await data_generator:
        data = {'_index': index_name, '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    return bulk_query

import pytest
import random

from starlette import status

from tests.functional.settings import test_settings
from tests.functional.utils.generator import FilmGenerator, generate_bulk_query


class TestFilmAPI:
    """ Класс для тестирования API фильмов. """
    film_generator = FilmGenerator()
    movie_index_name, movie_index_schema = test_settings.elastic.movie_index
    url = test_settings.service.url + '/api/v1/films'

    @staticmethod
    async def prepare_data(es_write_data, count):
        films_data = TestFilmAPI.film_generator.get_generated_data(count=count)
        bulk_query = await generate_bulk_query(index_name=TestFilmAPI.movie_index_name, data_generator=films_data)
        await es_write_data(TestFilmAPI.movie_index_name, TestFilmAPI.movie_index_schema, bulk_query)
        return bulk_query

    @staticmethod
    def truncate_sentence(sentence):
        """ Обрезает строку после первых трёх слов."""
        words = sentence.split()
        return ' '.join(words[:3])

    @pytest.mark.parametrize(
        'query_data, expected_answer',
        [
            (
                    {'genre': '6c162475-c7ed-4461-9184-001ef3d9f26e', 'page_size': 8, 'page_number': 4},
                    {'status': status.HTTP_200_OK, 'length': 6},
            ),
            (
                    {'genre': 'd566a651-86df-4566-8305-8cb1acc471d5'},
                    {'status': status.HTTP_200_OK, 'length': 0},
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_film_list(self, redis_client, es_write_data, make_get_request, query_data, expected_answer):
        """ Тест для проверки получения списка фильмов с параметрами. """
        await self.prepare_data(es_write_data, count=30)

        await redis_client.flushdb()

        response = await make_get_request(self.url, query_data)
        body, response_status_code = response.json(), response.status_code

        assert response_status_code == expected_answer['status']
        assert len(body) == expected_answer['length']

    @pytest.mark.asyncio
    async def test_get_film_detail(self, es_write_data, make_get_request):
        """ Тест для проверки получения деталей фильма по ID. """
        bulk_query = await self.prepare_data(es_write_data, count=3)

        film_id = bulk_query[random.randint(0, len(bulk_query) - 1)]['_id']

        response = await make_get_request(f"{self.url}/{film_id}", query_data=None)
        body = response.json()

        assert response.status_code == status.HTTP_200_OK, f'Ответ должен содержать статус код = {status.HTTP_200_OK}'
        assert isinstance(body, dict)
        assert body['id'] == film_id

    @pytest.mark.asyncio
    async def test_film_bad_sort(self, es_write_data, make_get_request):
        """ Тест для проверки обработки некорректного параметра сортировки. """
        await self.prepare_data(es_write_data, count=1)

        response = await make_get_request(self.url, query_data={'sort': 'wrong field'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST, f'Ответ должен содержать статус код = {status.HTTP_400_BAD_REQUEST}'

    @pytest.mark.asyncio
    async def test_film_cache(self, redis_client, es_write_data, make_get_request):
        """ Тест для проверки работы кеширования. """
        await self.prepare_data(es_write_data, count=1)
        await redis_client.flushdb()

        response = await make_get_request(self.url, query_data={'query': 'The Star'})
        keys = await redis_client.keys()
        await redis_client.aclose()

        assert response.status_code == status.HTTP_200_OK, f'Ответ должен содержать статус код = {status.HTTP_200_OK}'
        assert len(keys) == 1

    @pytest.mark.asyncio
    async def test_search_film_zero_response(self, es_write_data, make_get_request):
        """ Тест поиска по параметру, по которому должно быть найдено ноль подходящих фильмов. """
        response = await make_get_request(self.url + '/search', query_data={'query': 'asd123asd13'})
        assert response.status_code == status.HTTP_200_OK, f'Запрос должен возвращать статус код = {status.HTTP_200_OK}'
        assert len(response.json()) == 0, 'В ответе не должно быть результатов'

    @pytest.mark.asyncio
    async def test_search_film_by_description(self, es_write_data, make_get_request):
        """ Тест поиска фильма по описанию, созданного фильма. """
        bulk_query = await self.prepare_data(es_write_data, count=12)
        film_descr = bulk_query[0].get('_source').get('description')
        film_title = bulk_query[0].get('_source').get('title')
        # берём первые три слова из описания дла подстановки в качестве параметра в поиске
        search_condition = self.truncate_sentence(film_descr)

        response = await make_get_request(self.url + '/search', query_data={'query': search_condition})
        assert response.status_code == status.HTTP_200_OK, f'Запрос должен возвращать статус код = {status.HTTP_200_OK}'
        response_data = response.json()[0].get('title')
        assert response_data == film_title, 'Название фильма не совпадает с искомым по описанию'

    @pytest.mark.asyncio
    async def test_pagination_page_size_in_search_film(self, es_write_data, make_get_request):
        """ Тест поиска ограничения выдачи количества записей через параметрм page_size. """
        await self.prepare_data(es_write_data, count=100)
        filter_params = {
            'page_size': 30,
        }
        response = await make_get_request(self.url + '/search', filter_params)
        assert response.status_code == status.HTTP_200_OK, f'Запрос должен возвращать статус код = {status.HTTP_200_OK}'
        response_data = response.json()
        assert len(response_data) == 30, 'В ответе должно быть 30 результатов'

    @pytest.mark.asyncio
    async def test_pagination_page_default_value_size_in_search_film(self, es_write_data, make_get_request):
        """ Тест ограничения выдачи количества записей через параметр page_size с значением по умолчанию при поиске фильма. """
        await self.prepare_data(es_write_data, count=100)
        response = await make_get_request(self.url + '/search', {})
        assert response.status_code == status.HTTP_200_OK, f'Запрос должен возвращать статус код = {status.HTTP_200_OK}'
        response_data = response.json()
        assert len(response_data) == 12, 'В ответе должно быть 12 результатов'

    @pytest.mark.asyncio
    async def test_pagination_page_number_in_search_film(self, es_write_data, make_get_request):
        """ Тест ограничения выдачи количества записей через параметр page_number при поиске фильма. """
        await self.prepare_data(es_write_data, count=5)
        filter_params = {
            'page_number': 6,
        }
        response = await make_get_request(self.url + '/search', filter_params)
        assert response.status_code == status.HTTP_200_OK, f'Запрос должен возвращать статус код = {status.HTTP_200_OK}'
        response_data = response.json()
        assert len(response_data) == 0, 'В ответе должно быть 0 результатов'

    @pytest.mark.asyncio
    async def test_film_search_cache(self, redis_client, es_write_data, make_get_request):
        """ Тест для проверки работы кеширования. """
        await self.prepare_data(es_write_data, count=1)
        await redis_client.flushdb()

        response = await make_get_request(self.url + '/search', query_data={'query': 'film'})
        keys = await redis_client.keys()
        await redis_client.aclose()

        assert response.status_code == status.HTTP_200_OK, f'Ответ должен содержать статус код = {status.HTTP_200_OK}'
        assert len(keys) == 1, 'В кэше отсутствуют данные'

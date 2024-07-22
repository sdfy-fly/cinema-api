import http
import random

import pytest

from tests.functional.settings import test_settings
from tests.functional.utils.generator import PersonGenerator, FilmGenerator, generate_bulk_query

person_generator = PersonGenerator()
film_generator = FilmGenerator()


@pytest.mark.asyncio
async def test_person_list(redis_client, es_write_data, make_get_request):
    person_index_name, person_index_schema = test_settings.elastic.person_index

    persons_data = person_generator.get_generated_data(count=10)
    bulk_query = await generate_bulk_query(index_name=person_index_name, data_generator=persons_data)

    await es_write_data(person_index_name, person_index_schema, bulk_query)

    await redis_client.flushdb()

    url = test_settings.service.url + '/api/v1/persons'
    response = await make_get_request(url, query_data=None)
    body, status = response.json(), response.status_code

    assert status == http.HTTPStatus.OK
    assert len(body) == 10


@pytest.mark.asyncio
async def test_person_detail(es_write_data, make_get_request):
    person_index_name, person_index_schema = test_settings.elastic.person_index

    persons_data = person_generator.get_generated_data(count=20)
    bulk_query = await generate_bulk_query(index_name=person_index_name, data_generator=persons_data)
    person_id = bulk_query[random.randint(0, len(bulk_query) - 1)]['_id']

    await es_write_data(person_index_name, person_index_schema, bulk_query)

    url = test_settings.service.url + f'/api/v1/persons/{person_id}'
    response = await make_get_request(url, query_data=None)
    body, status = response.json(), response.status_code

    assert status == http.HTTPStatus.OK
    assert isinstance(body, dict)
    assert body['id'] == person_id


@pytest.mark.parametrize(
    'person_data, expected_answer',
    [
        (
                {'person_id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95'},
                {'status': http.HTTPStatus.OK, 'length': 10},
        ),
        (
                {'person_id': 'f09c267a-1a38-46c2-8b1a-35721b96ec34'},
                {'status': http.HTTPStatus.OK, 'length': 0},
        ),
        (
                {'person_id': '87fe6055-6fdf-43f8-9da0-c8167c6b1ee3'},
                {'status': http.HTTPStatus.NOT_FOUND, 'length': 1},
        ),
    ],
)
@pytest.mark.asyncio
async def test_films_by_person_list(redis_client, es_write_data, make_get_request, person_data, expected_answer):
    movie_index_name, movie_index_schema = test_settings.elastic.movie_index
    person_index_name, person_index_schema = test_settings.elastic.person_index

    films_data = film_generator.get_generated_data(count=expected_answer['length'])
    film_bulk_query = await generate_bulk_query(index_name=movie_index_name, data_generator=films_data)
    persons_data = person_generator.get_loaded_data(path='tests/functional/data/persons.json')
    person_bulk_query = await generate_bulk_query(index_name=person_index_name, data_generator=persons_data)

    await es_write_data(movie_index_name, movie_index_schema, film_bulk_query)
    await es_write_data(person_index_name, person_index_schema, person_bulk_query)

    await redis_client.flushdb()

    url = test_settings.service.url + f"/api/v1/persons/{person_data['person_id']}/films"
    response = await make_get_request(url, query_data=None)
    body, status = response.json(), response.status_code

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']


@pytest.mark.asyncio
async def test_person_cache(redis_client, es_write_data, make_get_request):
    person_index_name, person_index_schema = test_settings.elastic.person_index

    persons_data = person_generator.get_generated_data(count=20)
    bulk_query = await generate_bulk_query(index_name=person_index_name, data_generator=persons_data)
    person_id = bulk_query[random.randint(0, len(bulk_query) - 1)]['_id']

    await es_write_data(person_index_name, person_index_schema, bulk_query)

    await redis_client.flushdb()

    url = test_settings.service.url + f'/api/v1/persons/{person_id}'
    response = await make_get_request(url, query_data=None)

    keys = await redis_client.keys()
    await redis_client.aclose()

    assert response.status_code == http.HTTPStatus.OK
    assert len(keys) == 1
    assert keys[0].decode('utf-8') == f'person:{url}'


@pytest.mark.asyncio
async def test_person_search_cache(redis_client, es_write_data, make_get_request):
    """ Проверяет работу кэша в /search"""
    person_index_name, person_index_schema = test_settings.elastic.person_index

    persons_data = person_generator.get_generated_data(count=20)
    bulk_query = await generate_bulk_query(index_name=person_index_name, data_generator=persons_data)
    await es_write_data(person_index_name, person_index_schema, bulk_query)

    await redis_client.flushdb()

    url = test_settings.service.url + f'/api/v1/persons/search'
    response = await make_get_request(url, query_data=None)

    keys = await redis_client.keys()
    await redis_client.aclose()

    assert response.status_code == http.HTTPStatus.OK
    assert len(keys) == 1
    assert keys[0].decode('utf-8') == f'person_search:{url}'


@pytest.mark.asyncio
async def test_search_film_page_size(es_write_data, make_get_request):
    """ Проверяет работу параметра page_size в /search"""
    person_index_name, person_index_schema = test_settings.elastic.person_index

    persons_data = person_generator.get_generated_data(count=20)
    bulk_query = await generate_bulk_query(index_name=person_index_name, data_generator=persons_data)
    await es_write_data(person_index_name, person_index_schema, bulk_query)

    url = test_settings.service.url + f'/api/v1/persons/search'
    response = await make_get_request(url, query_data={'page_size': 5})
    body, status = response.json(), response.status_code

    assert status == http.HTTPStatus.OK, f'Запрос должен возвращать статус код = {http.HTTPStatus.OK}'
    assert len(body) == 5, 'Запрос с параметром page_size не ограничил количество записей в ответе'


@pytest.mark.asyncio
async def test_search_film_page_number(es_write_data, make_get_request):
    """ Проверяет работу параметра page_number в /search"""
    person_index_name, person_index_schema = test_settings.elastic.person_index

    persons_data = person_generator.get_generated_data(count=5)
    bulk_query = await generate_bulk_query(index_name=person_index_name, data_generator=persons_data)
    await es_write_data(person_index_name, person_index_schema, bulk_query)

    url = test_settings.service.url + f'/api/v1/persons/search'
    response = await make_get_request(url, query_data={'page_size': 1, 'page_number': 6})
    body, status = response.json(), response.status_code

    assert status == http.HTTPStatus.OK, f'Запрос должен возвращать статус код = {http.HTTPStatus.OK}'
    assert len(body) == 0, 'Запрос с параметром page_size не ограничил количество записей в ответе'


@pytest.mark.asyncio
async def test_person_search_name(es_write_data, make_get_request):
    """ Проверка поиска актёра по имени. """
    person_index_name, person_index_schema = test_settings.elastic.person_index

    persons_data = person_generator.get_generated_data(count=20)
    bulk_query = await generate_bulk_query(index_name=person_index_name, data_generator=persons_data)
    await es_write_data(person_index_name, person_index_schema, bulk_query)

    find_name = bulk_query[0].get('_source').get('name')

    url = test_settings.service.url + f'/api/v1/persons/search'
    response = await make_get_request(url, query_data={'query': find_name})

    assert response.status_code == http.HTTPStatus.OK
    assert  response.json()[0].get('name') == find_name, 'Неудовлетворительный результат поиска, необходимый актёр не найден'

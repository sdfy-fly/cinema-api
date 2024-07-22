import http
import random

import pytest

from tests.functional.settings import test_settings
from tests.functional.utils.generator import GenreGenerator, FilmGenerator, generate_bulk_query

genre_generator = GenreGenerator()
film_generator = FilmGenerator()


@pytest.mark.asyncio
async def test_genre_list(redis_client, es_write_data, make_get_request):
    genre_index_name, genre_index_schema = test_settings.elastic.genre_index

    genres_data = genre_generator.get_generated_data(count=10)
    bulk_query = await generate_bulk_query(index_name=genre_index_name, data_generator=genres_data)

    await es_write_data(genre_index_name, genre_index_schema, bulk_query)

    await redis_client.flushdb()

    url = test_settings.service.url + '/api/v1/genres'
    response = await make_get_request(url, query_data=None)
    body, status = response.json(), response.status_code

    assert status == http.HTTPStatus.OK
    assert len(body) == 10


@pytest.mark.asyncio
async def test_genre_detail(es_write_data, make_get_request):
    genre_index_name, genre_index_schema = test_settings.elastic.genre_index

    genres_data = genre_generator.get_generated_data(count=10)
    bulk_query = await generate_bulk_query(index_name=genre_index_name, data_generator=genres_data)
    genre_id = bulk_query[random.randint(0, len(bulk_query) - 1)]['_id']

    await es_write_data(genre_index_name, genre_index_schema, bulk_query)

    url = test_settings.service.url + f'/api/v1/genres/{genre_id}'
    response = await make_get_request(url, query_data=None)
    body, status = response.json(), response.status_code

    assert status == http.HTTPStatus.OK
    assert isinstance(body, dict)
    assert body['id'] == genre_id


@pytest.mark.parametrize(
    'genre_data, expected_answer',
    [
        (
                {'genre_id': '6c162475-c7ed-4461-9184-001ef3d9f26e'},
                {'status': http.HTTPStatus.OK, 'length': 4},
        ),
        (
                {'genre_id': 'b92ef010-5e4c-4fd0-99d6-41b6456272cd'},
                {'status': http.HTTPStatus.OK, 'length': 0},
        ),
        (
                {'genre_id': '347643d5-b88a-4680-b1c5-5ee2e41d2906'},
                {'status': http.HTTPStatus.NOT_FOUND, 'length': 1},
        ),
    ],
)
@pytest.mark.asyncio
async def test_films_by_genre_list(redis_client, es_write_data, make_get_request, genre_data, expected_answer):
    movie_index_name, movie_index_schema = test_settings.elastic.movie_index
    genre_index_name, genre_index_schema = test_settings.elastic.genre_index

    films_data = film_generator.get_generated_data(count=expected_answer['length'])
    film_bulk_query = await generate_bulk_query(index_name=movie_index_name, data_generator=films_data)
    genres_data = genre_generator.get_loaded_data(path='tests/functional/data/genres.json')
    genre_bulk_query = await generate_bulk_query(index_name=genre_index_name, data_generator=genres_data)

    await es_write_data(movie_index_name, movie_index_schema, film_bulk_query)
    await es_write_data(genre_index_name, genre_index_schema, genre_bulk_query)

    await redis_client.flushdb()

    url = test_settings.service.url + f"/api/v1/genres/{genre_data['genre_id']}/films"
    response = await make_get_request(url, query_data=None)
    body, status = response.json(), response.status_code

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']


@pytest.mark.asyncio
async def test_genre_cache(redis_client, es_write_data, make_get_request):
    genre_index_name, genre_index_schema = test_settings.elastic.genre_index

    genres_data = genre_generator.get_generated_data(count=20)
    bulk_query = await generate_bulk_query(index_name=genre_index_name, data_generator=genres_data)
    genre_id = bulk_query[random.randint(0, len(bulk_query) - 1)]['_id']

    await es_write_data(genre_index_name, genre_index_schema, bulk_query)

    await redis_client.flushdb()

    url = test_settings.service.url + f'/api/v1/genres/{genre_id}'
    response = await make_get_request(url, query_data=None)

    keys = await redis_client.keys()
    await redis_client.aclose()

    assert response.status_code == http.HTTPStatus.OK
    assert len(keys) == 1
    assert keys[0].decode('utf-8') == f'genre:{url}'

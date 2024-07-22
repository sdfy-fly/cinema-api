""""
Этот модуль предназначен для проверки доступности сервисов Elasticsearch и Redis перед выполнением тестов.
Он содержит функции, которые ожидают доступности каждого из сервисов, пытаясь установить соединение.
"""
import time

from elasticsearch import Elasticsearch
from redis import Redis

from tests.functional.settings import test_settings


def wait_for_es():
    """ Проверяет доступность Elasticsearch, пытаясь выполнить ping. """
    es_client = Elasticsearch(hosts=[test_settings.elastic.url])
    while True:
        if es_client.ping():
            break
        time.sleep(1)


def wait_for_redis():
    """ Проверяет доступность Redis, пытаясь выполнить ping. """
    redis_client = Redis(host=test_settings.redis.host, port=test_settings.redis.port)
    while True:
        if redis_client.ping():
            break
        time.sleep(1)


def run_waiters():
    """
    Запускает последовательность ожиданий для всех необходимых сервисов.
    В данном случае ожидает доступности Elasticsearch и Redis.
    """
    wait_for_es()
    wait_for_redis()


if __name__ == '__main__':
    run_waiters()

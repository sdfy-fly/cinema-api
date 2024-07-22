from src.models.film import Film
from src.serializers.films.base import BaseFilmSerializer


class ElasticFilmSerializer(BaseFilmSerializer):
    def serialize(self, data: dict) -> Film:
        return Film(**data['_source'])

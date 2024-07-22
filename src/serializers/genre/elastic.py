from src.models.genre import Genre, Film
from src.serializers.genre.base import BaseGenreSerializer


class ElasticGenreSerializer(BaseGenreSerializer):
    def serialize(self, data: dict) -> Genre:
        return Genre(**data['_source'])

    def serialize_movie(self, data: dict) -> Film:
        return Film(**data['_source'])

from src.models.person import Person, Film
from src.serializers.person.base import BasePersonSerializer


class ElasticPersonSerializer(BasePersonSerializer):
    def serialize(self, data: dict) -> Person:
        return Person(**data['_source'])

    def serialize_movie(self, data: dict) -> Film:
        return Film(**data['_source'])

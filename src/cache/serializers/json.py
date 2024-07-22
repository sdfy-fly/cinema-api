import json
from typing import Any, Type
from pydantic import BaseModel

from src.cache.serializers.base import BaseSerializer


class JsonSerializer(BaseSerializer):
    def serialize(self, data: Any) -> str:
        if isinstance(data, list):
            return json.dumps([item.json() for item in data])
        return data.json()

    def deserialize(self, data: str, model: Type[BaseModel]) -> Any:
        items = json.loads(data)
        if isinstance(items, list):
            return [model.parse_raw(item) for item in items]
        return model.parse_raw(data)

from bson import ObjectId

class MongoSerializer:
    def __init__(self, data):
        self.data = data

    def serialize(self):
        if isinstance(self.data, list):
            return [self._serialize_item(item) for item in self.data]
        elif isinstance(self.data, dict):
            return self._serialize_item(self.data)
        else:
            raise TypeError(f"Unsupported data type: {type(self.data)}")

    def _serialize_item(self, item):
        if isinstance(item, ObjectId):
            return str(item)
        elif isinstance(item, dict):
            return {key: self._serialize_item(value) for key, value in item.items()}
        else:
            return item
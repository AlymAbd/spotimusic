import json
from os import path
from app import DATA_PATH, generate_path


class BaseEntity(object):
    filename: str = None
    is_new: bool = True
    fields: dict = {}
    values: dict = {}
    original_values: dict = {}

    @classmethod
    def new(cls) -> 'BaseEntity':
        cls = cls()
        """This will overwrite exist json file"""
        for field in cls.fields:
            cls.set_value(field, cls.fields[field].get('default'))
        return cls

    @classmethod
    def load(cls) -> 'BaseEntity':
        cls = cls()
        if path.isfile(cls.get_filepath()):
            with open(cls.get_filepath(), 'r') as f:
                data = json.load(f)
                for field in cls.fields:
                    cls.set_value(field, data.get(field,
                                                  cls.fields[field].get('default')))
                    cls.original_values[field] = data.get(field)
                cls.is_new = False
                return cls
        else:
            return cls.new()

    def save(self):
        with open(self.get_filepath(), 'w') as f:
            json.dump(self.values, f)

    def delete(self) -> bool:
        prepared_values = {}
        for field_name in self.fields:
            prepared_values[field_name] = None

        with open(self.get_filepath(), 'w') as f:
            json.dump(prepared_values, f)
        return True

    def set_value(self, field, value):
        self.values[field] = value

    def get_filepath(self):
        return generate_path(DATA_PATH, self.filename) + '.json'

    def get(self, field, default=None):
        return self.values.get(field, default)

from abc import ABC, abstractclassmethod

class Model(ABC, object):
    _onerecord: bool = False
    _type: str = ''

    def validate(self):
        pass

    def serialize_in(self):
        pass

    def serialize_out(self):
        pass

    def get_columns(self) -> list:
        exlude = ['table_name']
        return [x for x in dir(self) if not x.startswith('_') and x not in exlude and not callable((getattr(self, x)))]

    @property
    def table_name(self):
        module = str(self.__class__.__module__).split('.')[-1].lower()
        classname = str(self.__class__.__name__).lower()
        return f"{module}__{classname}"


class OneRecordModel(Model):
    _onerecord: bool = True



class Column(ABC):
    _default_value = None
    _null = True
    _type = None
    _primary_key = False

    def __init__(self, default=None, nullable=True) -> None:
        self._default_value = default
        self._null = nullable
        super().__init__()

    @property
    def column_type(self):
        return self._type

    @property
    def nullable(self):
        return self._null

    @property
    def primary_key(self):
        return self._primary_key

    @property
    def default_value(self):
        return self._default_value


class String(Column):
    _type = 'TEXT'

class Integer(Column):
    _type = 'INTEGER'

class Decimal(Column):
    _type = 'REAL'
    _max_digits = None
    _places = None

    def __init__(self, max_digits, places, default="", nullable=True) -> None:
        self._max_digits = max_digits
        self._places = places
        super().__init__(default, nullable)

class Float(Column):
    _type = 'REAL'

class Datetime(Column):
    _type = 'DATETIME'

    def __init__(self, only_date = False, only_time = False, default="", nullable=True) -> None:
        super().__init__(default, nullable)

class Array(Column):
    _type = 'TEXT'

class Json(Column):
    _type = 'TEXT'

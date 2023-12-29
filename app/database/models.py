from abc import ABC, abstractclassmethod
from .entity import Entity
from .database import db_cursor

class Model(ABC, object):
    _onerecord: bool = False
    _type: str = ''
    _table_name: str = None
    _primary_key: str = None

    def get_columns(self) -> list:
        exlude = ['table_name']
        return [x for x in dir(self) if not x.startswith('_') and x not in exlude and not callable((getattr(self, x)))]

    @property
    def table_name(self):
        if self._table_name:
            return self._table_name
        else:
            module = str(self.__class__.__module__).split('.')[-1].lower()
            classname = str(self.__class__.__name__).lower()
            return f"{module}__{classname}"

    @classmethod
    def new_object(cls) -> Entity:
        obj = Entity(cls)
        return obj

    @classmethod
    def get_first(cls) -> 'Builder':
        builder = Builder(cls, 1, 0)
        return builder

    @classmethod
    def get_all(cls) -> 'Builder':
        builder = Builder(cls, 100, 0)
        return builder


class OneRecordModel(Model):
    _onerecord: bool = True


class Builder(object):
    model: Model = None

    _limit = 100
    _offset = 0
    _select = ['*']
    _where = []
    _ordering = []

    def __init__(self, model: Model, limit=100, offset=0) -> None:
        self.model = model()
        self.limit(limit, offset)

    def select(self, *columns):
        self._select = columns

    def limit(self, limit=100, offset=0):
        self._limit = limit
        self._offset = offset

    """
    use []list for OR logic
    use ()tuple for AND logic
    """
    def where(self, *where):
        self._where = self._handle_filter(where)

    def _handle_filter(self, where, operator='AND'):
        filters = "("
        i = 1
        for filter in where:
            if isinstance(filter, tuple):
                operator = 'AND'
                filters += self._handle_filter(filter, operator)
            elif isinstance(filter, list):
                operator = 'OR'
                filters += "(" + self._handle_filter(filter, operator) + ")"
            else:
                filters += f" {filter}"
            if i < len(where):
                filters += f" {operator} "
            i += 1
        filters += ")"
        return filters

    def order(self, *orderby):
        self._ordering = orderby

    def load(self, as_object = True):
        data = []
        cur = db_cursor.execute(self._generate_sql())
        rows = cur.fetchall()
        columns = [(x[0], x[1][0]) for x in enumerate(cur.description)]
        if not rows:
            rows = [[None for x in columns]]

        for row in rows:
            row = [(col, row[i]) for i, col in columns]
            if as_object:
                obj = Entity(self.model)
                obj.set_data(row)
                data.append(obj)
            else:
                values = {}
                for value in row:
                    values[value[0]] = value[1]
                data.append(values)
        if self._limit == 1 and len(data) > 0:
            data = data[0]
        return data

    def _generate_sql(self):
        if not self._select:
            raise ValueError("At least one column must be selected.")
        sql = "SELECT "
        sql += ", ".join(self._select)
        sql += f" FROM {self.model.table_name}"
        if self._where:
            sql += f" WHERE {self._where}"
        if self._ordering:
            sql += f" ORDER BY {', '.join(self._ordering)}"
        sql += f" LIMIT {self._limit} OFFSET {self._offset}"
        return sql


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

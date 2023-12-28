from .database import db_cursor, database

class Entity(object):
    model = None
    values = {}

    def __init__(self, model) -> None:
        if callable(model):
            self.model = model()

    def save(self):
        cur = db_cursor.execute(self._generate_sql())
        database.commit()
        self.values['id'] = cur.lastrowid
        self.id = cur.lastrowid
        return self.values

    def _serialize_to_save(self, column, value):
        pass

    def delete(self):
        pass

    def set_value(self, column, value):
        setattr(self, column, value)
        self.values[column] = value

    """
    Data list of array
    example [(column0, value0), (column1, value1)]
    """
    def set_data(self, data):
        for row in data:
            self.set_value(row[0], row[1])

    def _generate_sql(self):
        values = ""
        columns = self.model.get_columns()
        for column in columns:
            values += f"'{str(self.values[column])}',"
        values = values[:-1]
        columns = ", ".join([str(x) for x in columns])
        return f"INSERT INTO {self.model.table_name} ({columns}) VALUES ({values});"


from .database import db_cursor, database

class Entity(object):
    model = None
    pk: str = None
    values = {}

    def __init__(self, model) -> None:
        if callable(model):
            self.model = model()

    def save(self):
        cur = db_cursor.execute(self._get_sql())
        database.commit()
        if self.model.primary_key:
            self.pk = self.values[self.model.primary_key] = cur.lastrowid
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

    def _get_sql(self):
        from app.database.models import OneRecordModel

        res = ""
        if self.pk:
            res = self._generate_update_sql()
        elif isinstance(self.model, OneRecordModel):
            res = self._generate_onerow_update_sql()
        else:
            res = self._generate_insert_sql()
        return res

    def _generate_insert_sql(self):
        values = ""
        columns = self.model.get_columns()
        for column in columns:
            values += f"'{str(self.values[column])}',"
        values = values[:-1]
        columns = ", ".join([str(x) for x in columns])
        return f"INSERT INTO {self.model.table_name} ({columns}) VALUES ({values});"

    def _generate_update_sql(self):
        values = ""
        columns = self.model.get_columns()
        for column in columns:
            values += f"{column} = '{str(self.values[column])}',"
        values = values[:-1]
        return f"UPDATE {self.model.table_name} SET {values} WHERE {self.model.primary_key}={self.pk};"

    def _generate_onerow_update_sql(self):
        values = ""
        columns = self.model.get_columns()
        for column in columns:
            values += f"'{str(self.values[column])}',"
        values = values[:-1]
        columns = ", ".join([str(x) for x in columns])
        return f"INSERT INTO {self.model.table_name} ({columns}) VALUES ({values});"

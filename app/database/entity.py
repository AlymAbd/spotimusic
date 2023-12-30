from .database import db_cursor, database

class Entity(object):
    model = None
    pk: str = None
    values = {}
    old_values = {}
    is_new = False

    def __init__(self, model, is_new = False) -> None:
        self.values = {}
        self.old_values = {}
        self.pk = None
        self.model = model
        self.is_new = is_new

        if callable(model):
            self.model = model()

    def save(self):
        cur = db_cursor.execute(self._get_sql())
        database.commit()
        if self.model._primary_key:
            self.pk = self.values[self.model._primary_key] = cur.lastrowid
        return self.values

    def _serialize_to_save(self, column, value):
        pass

    def delete(self, id = None, custom: str = None):
        sql = f"DELETE FROM {self.model.table_name}"
        if custom:
            sql += f" WHERE {custom}"
        if id:
            sql += f" WHERE {self.model._primary_key}={id}"
        sql += ";"
        db_cursor.execute(sql)
        database.commit()
        return True

    def set_value(self, column, value):
        setattr(self, column, value)
        self.values[column] = value
        if not column in self.old_values.keys():
            self.old_values[column] = value

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
        if self.pk and not self.is_new:
            res = self._generate_update_sql()
        elif isinstance(self.model, OneRecordModel) and not self.is_new:
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
        self.delete()
        return self._generate_insert_sql()

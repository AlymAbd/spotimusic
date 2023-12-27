import app.models as models
from .models import Model
from inspect import isclass
from .database import db_cursor
import re

class Migration(Model):
    def start(self):
        migrations = self.get_migrations()
        for migration_name in migrations:
            instance = self.get_instance(migration_name)
            instance = instance()
            if isinstance(instance, Model):
                self.handle_table(instance)

    def exist_table(self, model: Model):
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        return False

    def update_table(self, model: Model):
        pass

    def delete_table(self, model: Model):
        pass

    def get_migrations(self):
        items = [x for x in dir(models) if not re.search("__", x) and self.is_class(x)]
        return items

    def is_class(self, name) -> bool:
        name = self.get_instance(name)
        return isclass(name)

    def get_instance(self, class_name):
        instance = getattr(models, class_name)
        return instance

    def handle_table(self, model: Model):
        if self.exist_table(model):
            self.update_table(model)
        else:
            self.create_table(model)

    def create_table(self, model: Model):
        columns = ""
        column_names = [x.lower() for x in model.get_columns()]
        for column_name in column_names:
            column = getattr(model, column_name)
            tmp = f"{column_name} {column.column_type}"
            if column.primary_key:
                tmp += " PRIMARY_KEY"
            if not column.nullable:
                tmp += " NOT NULL"
            if column.default_value:
                tmp += f" DEFAULT {column.default_value}"
            columns += f"{tmp},"
        columns = columns[:-1]
        ddl = f"CREATE table IF NOT EXISTS {model.table_name} ({columns})"
        db_cursor.execute(ddl)

    def generate_ddl(self, columns):
        for column in columns:
            column = column

from app.database.migration import Migration
from app.models import Migration as MigrationModel


class Migrations(Migration):
    model = MigrationModel

    def ddl(self):
        return f"""CREATE TABLE IF NOT EXISTS {self.model.table_name} (
            date DATETIME,
            migration_name TEXT,
            UNIQUE(migration_name)
        );"""

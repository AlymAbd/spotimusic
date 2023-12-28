from app.database.migration import Migration
from app.models import Secrets


class SecretsMigration(Migration):
    model = Secrets

    def ddl(self):
        return f"""CREATE TABLE IF NOT EXISTS {self.model.table_name} (
            client_id TEXT,
            redirect_uri TEXT,
            secret TEXT,
            state TEXT
        );"""


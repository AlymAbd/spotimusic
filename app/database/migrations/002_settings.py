from app.database.migration import Migration
from app.models import PlayerSettings, UserSettings


class UserSettingsMigration(Migration):
    model = UserSettings

    def ddl(self):
        return f"""CREATE TABLE IF NOT EXISTS {self.model.table_name} (
            music_cache_day_lifetime INT,
            language TEXT DEFAULT 'ENG',
            startup_page DEFAULT 'HOME'
        );"""


class PlayerSettingsMigration(Migration):
    model = PlayerSettings

    def ddl(self):
        return f"""CREATE TABLE IF NOT EXISTS {self.model.table_name} (
            volume INT,
            last_playlist_id INT,
            last_track_id INT
        );"""

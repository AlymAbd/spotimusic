from os import path, getcwd
import json
import base64


class BaseConfig(object):
    config_data :dict = None
    config_file :str = ''
    base_path: str = path.join(getcwd(), 'temp', 'config')

    def __init__(self) -> None:
        if self.file_exist():
            self.config_data = self.read()

    def read(self) -> dict:
        data = {}
        with open(path.join(self.base_path, self.config_file)) as f:
            data = json.loads(f.read())
        return data

    def file_exist(self):
        return path.isfile(self.path)

    def save(self) -> bool:
        self.write(self.config_data)

    def write(self, data: dict) -> bool:
        self.config_data = data
        write_type = 'a'
        if self.file_exist():
            write_type = 'w'
        with open(self.path, write_type) as f:
            json.dump(data, f)

    def get_data(self) -> dict:
        if self.config_data is None:
            return {}
        else:
            return self.config_data

    def set_value(self, key, value) -> None:
        if self.config_data is None:
            self.config_data = {}
        self.config_data[key] = value

    @property
    def path(self) -> str:
        return path.join(self.base_path, self.config_file)


class AuthConfig(BaseConfig):
    config_file = 'oauth.json'

    def __init__(self) -> None:
        super().__init__()

    def is_authorized(self) -> bool:
        return self.file_exist() and self.config_data.get('access_token')


class PlayerConfig(BaseConfig):
    config_file = 'settings.json'

    def __init__(self) -> None:
        super().__init__()
        if not self.file_exist():
            data = {
                "music_cache_day_lifetime": 365,
                "language": "EN",
                "_languages": ["EN", "CZ", "RU"],
                "startup_page": "last_playlist",
                "_startup_pages": ["last_playlist", "playlists"]
            }
            self.write(data)


class UserConfig(BaseConfig):
    config_file = 'user_settings.json'

    def __init__(self) -> None:
        super().__init__()
        if not self.file_exist():
            data = {
                "volume": 50,
                "last_playlist_id": None,
                "last_track_id": None
            }
            self.write(data)


class SpotifyConfig(BaseConfig):
    config_file = 'spotify_config.json'

    def read(self) -> dict:
        data = {}
        with open(self.path) as f:
            data = base64.a85decode(f.read())
            data = json.loads(data)
        return data

    def write(self, data: dict) -> bool:
        write_type = 'a'
        if self.file_exist():
            write_type = 'w'
        with open(self.path, write_type) as f:
            data = json.dumps(data)
            f.write(base64.a85decode(data))



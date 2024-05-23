from app.core.base_entity import BaseEntity


class UserSettings(BaseEntity):
    fields = {
        'theme': {},
        'language': {},
        'startup_page': {'default': 'home'},
        'audio_cache_lifetime': {'default': 30},
        'debug': {'default': False}
    }

    filename = 'user_settings'


class PlayerSettings(BaseEntity):
    fields = {
        'shuffle': {'default': False},
        'volume': {'default': 50},
        'repeat': {'default': False},
        'last_track_id': {},
        'last_playlist_id': {}
    }

    filename = 'player_settings'

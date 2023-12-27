from ..database import models

class UserSettings(models.OneRecordModel):
    """
    Settings in gui
    """
    music_cache_day_lifetime = models.Integer()
    language = models.String()
    startup_page = models.String()


class PlayerSettings(models.OneRecordModel):
    """
    Contains last user settings as last volume position, last track, last playlist etc
    """
    volume = models.Integer()
    last_playlist_id = models.Integer()
    last_track_id = models.Integer()

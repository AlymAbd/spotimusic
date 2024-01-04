from spotipy.oauth2 import SpotifyPKCE, SpotifyOAuth
from spotipy import Spotify


class Client(object):
    SCOPE = 'user-read-private user-library-read playlist-read-private playlist-read-collaborative'
    SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
    SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'

    client = None
    spotify_oauth = None

    def __init__(self) -> None:
        self.init_oauth_client()
        self.client = Spotify(auth_manager=self.spotify_oauth)

    def init_oauth_client(self, hard_reset: bool = False):
        from .models import Secrets
        from app import OAUTH_FILE_PATH

        if not self.spotify_oauth or hard_reset:
            secrets = Secrets.get_first()
            secrets = secrets.load()

            if secrets.secret:
                spotify_oauth = SpotifyOAuth(
                    secrets.client_id,
                    secrets.secret,
                    secrets.redirect_uri,
                    self.secrets.state,
                    self.SCOPE,
                    OAUTH_FILE_PATH,
                    open_browser=False
                )
            else:
                spotify_oauth = SpotifyPKCE(
                    secrets.client_id,
                    secrets.redirect_uri,
                    secrets.state,
                    self.SCOPE,
                    OAUTH_FILE_PATH,
                    open_browser=False
                )
            self.spotify_oauth = spotify_oauth
        return self.spotify_oauth

    @property
    def spotify(self):
        if not self.client:
            self.client = Spotify(auth_manager=self.spotify_oauth)
        return self.client

    def is_expired(self):
        token_info = self.spotify_oauth.get_cached_token()
        if not token_info or self.spotify_oauth.is_token_expired(token_info):
            return True
        return False

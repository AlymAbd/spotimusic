from spotipy.oauth2 import SpotifyPKCE, SpotifyOAuth
from spotipy import Spotify
from .models import Secrets
from app import OAUTH_FILE_PATH


secrets = Secrets.get_first()
secrets = secrets.load()

SCOPE = 'user-read-private'

CLIENT_ID = secrets.client_id
REDIRECT_URI = secrets.redirect_uri
STATE = secrets.state
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'

if secrets.secret:
    spotify_oauth = SpotifyOAuth(
        CLIENT_ID,
        secrets.secret,
        REDIRECT_URI,
        STATE,
        SCOPE,
        OAUTH_FILE_PATH,
        open_browser=False
    )
else:
    spotify_oauth = SpotifyPKCE(
    CLIENT_ID,
    REDIRECT_URI,
    STATE,
    SCOPE,
    OAUTH_FILE_PATH,
    open_browser=False
)

client = Spotify(auth_manager=spotify_oauth)

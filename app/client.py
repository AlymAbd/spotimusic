from spotipy.oauth2 import SpotifyPKCE
from spotipy import Spotify
import os

# Spotify API credentials
CLIENT_ID = '2845a9513fac4927bd3e4125b8a20d50'
REDIRECT_URI = 'http://0.0.0.0:6789/callback'
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
STATE = '01bscdX9j3o4aDFyyY13zXYLbAwZB9v0'
SCOPE = 'user-read-private'

spotify_oauth = SpotifyPKCE(
    CLIENT_ID,
    REDIRECT_URI,
    STATE,
    SCOPE,
    os.path.join(os.getcwd(), 'temp', 'config', 'oauth.json'),
    open_browser=False
)

client = Spotify(auth_manager=spotify_oauth)

from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify

# Spotify API credentials
SPOTIPY_CLIENT_ID = '2845a9513fac4927bd3e4125b8a20d50'
SPOTIPY_CLIENT_SECRET = '3e0683b1962548409b01218aee0098bc'
SPOTIPY_REDIRECT_URI = 'http://localhost:8000'

# Spotify OAuth token

def client(scope='playlist-read-private'):
    sp_oauth = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope)
    return Spotify(auth_manager=sp_oauth)

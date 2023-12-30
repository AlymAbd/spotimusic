from app import OAUTH_FILE_PATH, KILL_THREAD_PATH
from .models import Secrets
from os import path, remove


def secret_exist():
    secrets = Secrets.get_first()
    secrets = secrets.load()
    return secrets.client_id

def config_exist():
    return path.isfile(OAUTH_FILE_PATH)

def kill_thread():
    return path.isfile(KILL_THREAD_PATH)

def spotify_logout():
    return remove(OAUTH_FILE_PATH)

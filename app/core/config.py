from app import OAUTH_FILE_PATH
from os import path, remove
from app.core.entities.auth import Secrets


def secret_exist():
    secrets = Secrets.load()
    return secrets.get('client_id')


def config_exist():
    return path.isfile(OAUTH_FILE_PATH)


def spotify_logout():
    return remove(OAUTH_FILE_PATH)

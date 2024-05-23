from os import path, getcwd

ROOT_PATH = getcwd()
APP_PATH = path.join(ROOT_PATH, 'app')
CACHE_PATH = path.join(ROOT_PATH, 'cache')
RESOURCE_PATH = path.join(ROOT_PATH, 'resource')

RESOURCE_IMAGE_PATH = path.join(RESOURCE_PATH, 'images')
RESOURCE_ICON_PATH = path.join(RESOURCE_PATH, 'icons')

CACHE_MUSIC_PATH = path.join(CACHE_PATH, 'audio')
CACHE_IMAGE_PATH = path.join(CACHE_PATH, 'images')

DATA_PATH = path.join(CACHE_PATH, 'data')
OAUTH_FILE_PATH = path.join(DATA_PATH, 'oauth.json')


def generate_path(level: str = APP_PATH, pathes: tuple | str = ()) -> str:
    if isinstance(pathes, str):
        pathes = [pathes]
    return path.join(level, *pathes)

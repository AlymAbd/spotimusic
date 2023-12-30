from os import path, getcwd

ROOT_PATH = getcwd()
APP_PATH = path.join(ROOT_PATH, 'app')
TEMP_PATH = path.join(ROOT_PATH, 'temp')
RESOURCE_PATH = path.join(ROOT_PATH, 'resource')
RESOURCE_IMAGE_PATH = path.join(RESOURCE_PATH, 'images')
RESOURCE_ICON_PATH = path.join(RESOURCE_PATH, 'icons')
MUSIC_CACHE_PATH = path.join(TEMP_PATH, 'tracks')
OAUTH_FILE_PATH = path.join(TEMP_PATH, 'database', 'oauth.json')
KILL_THREAD_PATH = path.join(TEMP_PATH, 'kill_thread')


def generate_path(level: str = APP_PATH, pathes: tuple|str = ()) -> str:
    if isinstance(pathes, str):
        pathes = [pathes]
    return path.join(level, *pathes)

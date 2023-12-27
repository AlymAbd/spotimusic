from os import path, getcwd

ROOT_PATH = getcwd()
APP_PATH = path.join(ROOT_PATH, 'app')
TEMP_PATH = path.join(ROOT_PATH, 'temp')

def generate_path(level: str = APP_PATH, pathes: tuple = ()) -> str:
    return path.join(level, *pathes)

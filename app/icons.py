from app import RESOURCE_ICON_PATH
from os import path

class Icons(object):
    _fpath = ''

    def __init__(self, name: str) -> None:
        folder, filename = name.split('.')

        self._fpath = path.join(RESOURCE_ICON_PATH, folder, f"{filename}.svg")

    @property
    def str(self):
        return self._fpath

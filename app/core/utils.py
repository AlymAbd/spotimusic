import uuid
from app import CACHE_IMAGE_PATH, RESOURCE_ICON_PATH, RESOURCE_IMAGE_PATH
from os import path


def random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4())  # Convert UUID format to a Python string.
    random = random.upper()  # Make all characters uppercase.
    random = random.replace("-", "")  # Remove the UUID '-'.
    return random[0:string_length]  # Return the random string.


class AlbumCover(object):
    @classmethod
    def cover_exist(cls, album_id=None, file_name=None, file_path=None):
        ret = False
        if album_id:
            ret = path.isfile(
                path.join(CACHE_IMAGE_PATH, album_id + '.jpg')
            )
        elif file_name:
            ret = path.isfile(
                path.join(CACHE_IMAGE_PATH, file_name)
            )
        elif file_path:
            ret = path.isfile(file_path)
        return ret

    @classmethod
    def get_path(cls, album_id, default: bool = False):
        if default:
            if cls.cover_exist(album_id=album_id):
                ret = path.join(CACHE_IMAGE_PATH, album_id + '.jpg')
            else:
                ret = path.join(RESOURCE_IMAGE_PATH,
                                'default_image_cover.jpeg')
            return ret
        else:
            return path.join(CACHE_IMAGE_PATH, album_id + '.jpg')


class Icons(object):
    _fpath = ''

    def __init__(self, name: str) -> None:
        folder, filename = name.split('.')

        self._fpath = path.join(RESOURCE_ICON_PATH, folder, f"{filename}.svg")

    @property
    def str(self):
        return self._fpath

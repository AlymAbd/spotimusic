import uuid
from app import TEMP_PATH, RESOURCE_IMAGE_PATH
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
                path.join(TEMP_PATH, 'images', album_id + '.jpg')
            )
        elif file_name:
            ret = path.isfile(
                path.join(TEMP_PATH, 'images', file_name)
            )
        elif file_path:
            ret = path.isfile(file_path)
        return ret

    @classmethod
    def get_path(cls, album_id, default: bool = False):
        if default:
            if cls.cover_exist(album_id=album_id):
                ret = path.join(TEMP_PATH, 'images', album_id + '.jpg')
            else:
                ret = path.join(RESOURCE_IMAGE_PATH,
                                'default_image_cover.jpeg')
            return ret
        else:
            return path.join(TEMP_PATH, 'images', album_id + '.jpg')

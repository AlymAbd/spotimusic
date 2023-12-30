import requests
import threading
from threading import Thread
from PyQt6.QtCore import QObject, QUrl, Qt, QThread, pyqtSignal
from app import MUSIC_CACHE_PATH, TEMP_PATH, RESOURCE_IMAGE_PATH
from os import path
from pytube import YouTube, Search


class WorkerA(QThread):
    update_signal = pyqtSignal(dict)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.type = args[0] if args else None
        self.track_data = kwargs.get('kwargs')
        self._stop_flag = False

    def run(self):
        match self.type:
            case 'update_cover':
                if self.download_album_cover(self.track_data):
                    self.track_data['download_cover_success'] = True
                self.update_signal.emit(self.track_data)
            case 'play_track':
                if self.download_track(self.track_data):
                    self.track_data['download_track_success'] = True
                self.update_signal.emit(self.track_data)
        self.stop()

    def stop(self):
        self._stop_flag = True

    def download_album_cover(self, track_data):
        response = requests.get(track_data['album_image_url'])
        if response.status_code == 200:
            with open(track_data['album_localpath'], 'wb') as file:
                file.write(response.content)
            return True

    def download_track(self, track_data):
        file_path = path.join(MUSIC_CACHE_PATH, track_data['id'] + '.mp3')
        if not path.isfile(file_path):
            search = Search(
                track_data["main_artist_name"] + ": " + track_data["name"])
            results = search.results
            result = results[0].watch_url
            stream = YouTube(result)
            stream = stream.streams.filter(only_audio=True).first()
            stream.download(MUSIC_CACHE_PATH, track_data['id'] + '.mp3')
            return True

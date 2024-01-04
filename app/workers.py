import requests
from app import MUSIC_CACHE_PATH
from os import path
from PyQt6.QtCore import QThread, pyqtSignal
from pytube import YouTube, Search


class WorkerA(QThread):
    update_signal = pyqtSignal(dict)
    busy_signal = pyqtSignal(bool)

    run_type: str = None
    track_data: dict = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self._stop_flag = False

    def set_data(self, run_type, data: list) -> None:
        self.run_type = run_type
        self.track_data = data

    def run(self):
        match self.run_type:
            case 'update_cover':
                if self.download_album_cover(self.track_data):
                    self.track_data['download_cover_success'] = True
                self.update_signal.emit(self.track_data)
            case 'play_track':
                self.busy_signal.emit(True)
                if self.download_track(self.track_data):
                    self.track_data['download_track_success'] = True
                self.update_signal.emit(self.track_data)
                self.busy_signal.emit(False)
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


class WorkerB(WorkerA):
    pass


class WorkerC(WorkerA):
    pass

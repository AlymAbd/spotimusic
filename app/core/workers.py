import requests
from app import CACHE_MUSIC_PATH
from os import path
from PyQt6.QtCore import QThread, pyqtSignal
from pytube import YouTube, Search


class WorkerA(QThread):
    update_signal = pyqtSignal(dict)
    busy_signal = pyqtSignal(bool)

    run_type: str = None
    track_data: dict = None
    wait_event = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self._stop_flag = False

    def set_data(self, run_type, data: list, wait_event=None) -> None:
        self.run_type = run_type
        self.track_data = data
        self.wait_event = wait_event

    def run(self):
        self.busy_signal.emit(True)
        match self.run_type:
            case 'update_cover':
                if self.download_album_cover(self.track_data):
                    self.track_data['download_cover_success'] = True
                self.update_signal.emit(self.track_data)
            case 'play_track':
                if self.download_track(self.track_data):
                    self.track_data['download_track_success'] = True
                self.update_signal.emit(self.track_data)
            case 'download_all':
                if self.track_data.get('stop') == True:
                    self._stop_flag = True
                else:
                    self.download_all(self.track_data)
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
        import tempfile
        import shutil
        import requests

        file_path = path.join(CACHE_MUSIC_PATH, track_data['id'] + '.mp3')
        if not path.isfile(file_path):
            temp_path = path.join(tempfile.gettempdir(),
                                  track_data['id'] + '.mp3')
            search = Search(
                f"{track_data["main_artist_name"]} {track_data["name"]} audio music")
            results = search.results
            result = results[0].watch_url
            stream = YouTube(result)
            stream = stream.streams.filter(only_audio=True).first()

            stream = [x for x in stream.streaming_data['adaptiveFormats']
                      if 'audio/mp4' in x['mimeType'] and 'MEDIUM' in x['audioQuality']][0]

            req = requests.get(stream['url'])
            with open(temp_path, 'wb') as file:
                file.write(req.content)
                shutil.move(temp_path, file_path)
            return True

    def download_all(self, track_list: list):
        for track in track_list['list']:
            if self.wait_event.is_set():
                self.download_track(track)
                self.update_signal.emit(track)
            else:
                print('Stopping')
                break


class WorkerB(WorkerA):
    pass


class WorkerC(WorkerA):
    pass

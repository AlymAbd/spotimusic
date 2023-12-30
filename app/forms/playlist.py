import os
import asyncio
from os import path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel, QHBoxLayout, QSlider, QSplitter, QListWidgetItem, QStyle, QGridLayout
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QObject, QUrl, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPicture, QPixmap
from pytube import YouTube, Search
from app import MUSIC_CACHE_PATH, TEMP_PATH
from threading import Thread
import requests
import threading


class WorkerA(QThread):
    update_signal = pyqtSignal(dict)

    def __init__(self, target, *args, **kwargs) -> None:
        super().__init__()
        self.target = target
        self.type = args[0] if args else None
        self.track_data = kwargs.get('kwargs')
        self._stop_flag = False

    def run(self):
        result = self.target(self.track_data)
        if result:
            match self.type:
                case 'update_cover':
                    self.update_signal.emit(self.track_data)
                case _:
                    self.update_signal.emit(self.track_data)
        self.stop()

    def stop(self):
        self._stop_flag = True

def async_download_album_cover(track_data):
    response = requests.get(track_data['album_image_url'])
    if response.status_code == 200:
        with open(track_data['album_localpath'], 'wb') as file:
            file.write(response.content)
        return True

def async_download_track(track_data):
    file_path = path.join(MUSIC_CACHE_PATH, track_data['id'] + '.mp3')
    if not path.isfile(file_path):
        search = Search(track_data["name"])
        results = search.results
        result = results[0].watch_url
        stream = YouTube(result)
        stream = stream.streams.filter(only_audio=True).first()
        stream.download(MUSIC_CACHE_PATH, track_data['id'] + '.mp3')
        return True


class Playlist(QWidget):
    media_player = None
    audio_output = None
    client = None

    def __init__(self, parent: QWidget | None) -> None:
        from app.client import client
        self.client = client

        super().__init__(parent = parent)
        self.setMinimumSize(550, 600)
        self.setGeometry(550, 600, 500, 500)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        self.layout = QVBoxLayout()
        self.label_main = QLabel('Playlist')
        self.label_current_track = QLabel('... ... ...')

        media_control_widget = QWidget(self)
        media_control_layout = QHBoxLayout()
        self.media_control = MediaControl(media_control_widget)
        self.track_control = TrackControl(media_control_widget)

        self.slider_volume = QSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setMinimumSize(50, 20)
        self.slider_volume.setMaximumSize(150, 20)
        self.slider_volume.valueChanged.connect(self.change_volume)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(50)

        media_control_layout.addWidget(self.slider_volume)
        media_control_layout.addWidget(self.media_control, alignment=Qt.AlignmentFlag.AlignCenter)
        media_control_layout.addWidget(self.track_control, alignment=Qt.AlignmentFlag.AlignRight)

        media_control_widget.setLayout(media_control_layout)

        self.media_list = PlaylistList(self)
        self.audio_control = AudioControl(self)

        self.layout.addWidget(self.label_main)
        self.layout.addWidget(self.media_list)
        self.layout.addWidget(QSplitter())
        self.layout.addWidget(self.label_current_track, alignment=Qt.AlignmentFlag.AlignBottom)
        self.layout.addWidget(media_control_widget, alignment=Qt.AlignmentFlag.AlignBottom)
        self.layout.addWidget(self.audio_control, alignment=Qt.AlignmentFlag.AlignBottom)

        self.setLayout(self.layout)

    def change_volume(self, value):
        self.audio_volume = value
        self.audio_output.setVolume(value)


class MusicList(QWidget):
    """
    Track list
    """
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent = parent)
        self.layout = QVBoxLayout()
        self.playlist = QListWidget()
        self.layout.addWidget(self.playlist)
        self.setLayout(self.layout)

class PlaylistList(QWidget):
    client = None
    media_player = None
    current_music = {}
    current_playlist = None

    """
    Playlist, suggestions, albums
    """
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent = parent)

        self.stop_worker = threading.Event()
        self.client = parent.client
        self.media_player = parent.media_player

        self.layout = QHBoxLayout()

        self.playlist = QListWidget()
        self.playlist.setMinimumSize(100, 100)

        self.album_cover = QLabel()

        self.layout.addWidget(self.playlist)
        self.layout.addWidget(self.album_cover)
        self.setLayout(self.layout)
        self.render_playlist()
        self.playlist.itemDoubleClicked.connect(self.handle_click)

    def update_album_cover(self, track_data):
        picture = QPixmap()
        self.album_cover.setPixmap(picture)
        if path.isfile(track_data['album_localpath']):
            picture = QPixmap(track_data['album_localpath'])
            self.album_cover.setPixmap(picture)

    def handle_click(self, item):
        item_data = item.data(Qt.ItemDataRole.UserRole)
        item_text = item.text()
        item_data['name'] = item_text

        match item_data['type']:
            case 'track':
                item_data['album_localpath'] = path.join(TEMP_PATH, 'images', item_data['album_id'] + '.jpg')
                if not path.isfile(item_data['album_localpath']):
                    self.download_cover(item_data)
                self.play_selected_music(item_data)
            case 'playlist':
                self.load_playlist(item_data)
            case _:
                self.render_playlist()

    def render_playlist(self):
        result = self.client.current_user_playlists()
        self.playlist.clear()
        for playlist in result['items']:
            item = QListWidgetItem()
            item.setText(playlist['name'])
            item.setData(Qt.ItemDataRole.UserRole, {'id': playlist['id'], 'type': 'playlist'})
            self.playlist.addItem(item)

    def load_playlist(self, playlist_data):
        self.current_playlist = playlist_data
        self.setWindowTitle(playlist_data['name'])
        result = self.client.playlist_tracks(playlist_data['id'])
        self.playlist.clear()
        for track in result['items']:
            item = QListWidgetItem()
            item.setText(f"{track['track']['artists'][0]['name']}: {track['track']['name']}")
            item.setData(Qt.ItemDataRole.UserRole, {
                'id': track['track']['id'],
                'type': 'track',
                'album_id': track['track']['album']['id'],
                'album_image_url': track['track']['album']['images'][0]['url']
            })
            self.playlist.addItem(item)
        self.parent().label_current_track.setText(f'Music List ({self.playlist.count()})')

    def play_selected_music(self, track_data):
        self.parent().label_current_track.setText(f'(*caching*) {track_data["name"]}')
        self.parent().media_control.media_stop()
        self.update_album_cover(track_data)
        self.current_music = track_data
        self.setWindowTitle(self.current_playlist['name'] + ': ' + self.current_music['name'])
        file_path = path.join(MUSIC_CACHE_PATH, track_data['id'] + '.mp3')

        if not path.isfile(file_path):
            self.download_worker = WorkerA(async_download_track, 'play_track', kwargs=track_data)
            self.download_worker.update_signal.connect(self.play_selected_music)
            self.download_worker.start()
            return

        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.media_player.play()
        self.parent().label_current_track.setText(track_data["name"])
        # self.button_play_pause.setIcon(QIcon.fromTheme('media-playback-pause'))

    def download_cover(self, track_data):
        self.download_worker = WorkerA(async_download_album_cover, 'update_cover', kwargs=track_data)
        self.download_worker.update_signal.connect(self.update_album_cover)
        self.download_worker.start()


class MediaControl(QWidget):
    grandparent: QWidget = None

    """
    Buttons next, prev, play, pause, stop, add/remove to favorite
    """
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent = parent)
        self.grandparent = parent.parent()
        self.layout = QHBoxLayout()

        self.button_next = QPushButton()
        self.button_next.setIcon(QIcon.fromTheme('media-skip-forward'))
        self.button_next.setMaximumSize(50, 50)
        self.button_next.setMinimumSize(30, 30)
        self.button_next.clicked.connect(self.media_next)

        self.button_prev = QPushButton()
        self.button_prev.setIcon(QIcon.fromTheme('media-skip-backward'))
        self.button_prev.setMaximumSize(50, 50)
        self.button_prev.setMinimumSize(30, 30)
        self.button_prev.clicked.connect(self.media_prev)

        self.button_play_pause = QPushButton()
        self.button_play_pause.setIcon(QIcon.fromTheme('media-playback-start'))
        self.button_play_pause.setMaximumSize(60, 60)
        self.button_play_pause.setMinimumSize(35, 35)
        self.button_play_pause.clicked.connect(self.media_playpause)

        self.button_stop = QPushButton()
        self.button_stop.setIcon(QIcon.fromTheme('media-playback-stop'))
        self.button_stop.setMaximumSize(60, 60)
        self.button_stop.setMinimumSize(35, 35)
        self.button_stop.clicked.connect(self.media_stop)

        self.layout.addWidget(self.button_prev)
        self.layout.addWidget(self.button_stop)
        self.layout.addWidget(self.button_play_pause)
        self.layout.addWidget(self.button_next)

        self.setLayout(self.layout)

    def media_stop(self):
        self.grandparent.media_player.stop()

    def media_playpause(self, value):
        if value:
            self.grandparent.media_player.play()
        else:
            self.grandparent.media_player.pause()

    def media_next(self):
        pass

    def media_prev(self):
        pass

    def _change_track(self, index):
        self.stop_music()
        nextItem = self.music_list.item(index)
        nextItem.setSelected(True)
        self.music_list.setCurrentItem(nextItem)
        self.play_selected_music(nextItem)

    def next_track(self):
        currentIndex = self.music_list.indexFromItem(self.music_list.currentItem()).row()
        nextIndex = currentIndex + 1
        if (nextIndex + 1) > self.music_list.count():
            nextIndex = 0
        self._change_track(nextIndex)

    def previous_track(self):
        currentIndex = self.music_list.indexFromItem(self.music_list.currentItem()).row()
        nextIndex = currentIndex - 1
        if (nextIndex < 0):
            nextIndex = self.music_list.count() - 1
        self._change_track(nextIndex)

    def stop_music(self):
        if not self.playlist_loaded:
            self.current_music_label.setText('')
            self.media_player.stop()
            self.music_in_progress = True
            self.pause_play_music()


class TrackControl(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent = parent)

        self.layout = QHBoxLayout()

        self.button_add = QPushButton()
        self.button_add.setIcon(QIcon.fromTheme('zoom-in'))
        self.button_add.setMaximumSize(30, 30)

        self.button_mute = QPushButton()
        self.button_mute.setIcon(QIcon.fromTheme('audio-volume-muted'))
        self.button_mute.setMaximumSize(30, 30)

        self.layout.addWidget(self.button_add)
        self.layout.addWidget(self.button_mute)

        self.setLayout(self.layout)

class AudioControl(QWidget):
    """
    Track position, track info
    """
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent = parent)
        self.layout = QHBoxLayout()
        self.label = QLabel('0:00')
        self.slider_position = QSlider(Qt.Orientation.Horizontal)
        self.slider_position.setMinimumSize(100, 10)
        self.slider_position.setMaximum(100)
        self.slider_position.setMinimum(0)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.slider_position)
        self.setLayout(self.layout)

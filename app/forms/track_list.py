import requests
from os import path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QHBoxLayout, QSplitter, QListWidgetItem, QPushButton
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon
from app import MUSIC_CACHE_PATH, TEMP_PATH
from app.workers import WorkerA, WorkerB
from app.models import PlayerSettings
from app.icons import Icons
from app.util import AlbumCover
from app.forms.multilabel import MultiLabelWidget
from app.forms.media_control import MediaControl
from app.forms.current_track import CurrentTrack
from spotipy import Spotify


class TrackList(QWidget):
    client = None
    media_player = None
    current_music = {}
    current_playlist = {}
    scrollbar_last_value = 0

    _offset = 0
    limit = 100

    prev_page_exist: bool = False
    next_page_exist: bool = True

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)

        self.client: Spotify = parent.client
        self.media_player = parent.media_player

        self.layout = QHBoxLayout()

        self.playlist = QListWidget()

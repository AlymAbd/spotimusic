from PyQt6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout, QSplitter, QStatusBar
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import Qt
from spotipy import Spotify
from app.core.entities.settings import PlayerSettings
from .forms import MediaControl, TopPlaylistBar, TrackList, Playlist


class MediaList(QWidget):
    media_player = None
    audio_output = None
    client: Spotify = None
    current_volume: int = 50
    player_settings_data: PlayerSettings = None

    top_bar = None
    playlist: Playlist = None
    track_list: TrackList = None
    media_control = None
    status_bar = None
    layout = None

    def __init__(self, parent: QWidget = None) -> None:
        from app.core.client import Client

        super().__init__(parent=parent)
        self.parent = parent

        self.client = Client().spotify
        self.player_settings_data = PlayerSettings().load()
        self.current_volume = self.player_settings_data.get('volume', 50)

        self.setMinimumSize(800, 600)
        self.setGeometry(550, 600, 500, 500)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        layout = QVBoxLayout()
        self.stacked = QStackedWidget()

        self.top_bar = TopPlaylistBar(self)
        self.playlist = Playlist(self)
        self.track_list = TrackList(self)
        self.status_bar = QStatusBar()

        media_control_widget = QWidget(self)
        media_control_layout = QHBoxLayout()

        self.media_control = MediaControl(media_control_widget)

        media_control_layout.addWidget(
            self.media_control, alignment=Qt.AlignmentFlag.AlignCenter)

        media_control_widget.setLayout(media_control_layout)

        self.stacked.addWidget(self.playlist)
        self.stacked.addWidget(self.track_list)

        layout.addWidget(self.top_bar)
        layout.addWidget(QSplitter())
        layout.addWidget(self.stacked)
        layout.addWidget(QSplitter())
        layout.addWidget(media_control_widget,
                         alignment=Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(self.status_bar)

        self.media_player.mediaStatusChanged.connect(
            self.media_control.track_control.handle_next_track_behaviour
        )

        self.playlist.playlist.itemDoubleClicked.connect(
            self.handle_playlist_click
        )

        self.top_bar.button_back.clicked.connect(
            self.handle_back_button
        )

        self.setLayout(layout)

    """Save user settings before closing"""

    def closeEvent(self, event) -> None:
        self.player_settings_data.set_value('volume', self.current_volume)
        current_track_id = self.track_list.current_track.get('id')
        current_playlist_id = self.playlist.current_playlist.get('id')
        self.player_settings_data.set_value(
            'last_playlist_id', current_playlist_id)
        self.player_settings_data.set_value('last_track_id', current_track_id)
        self.player_settings_data.save()
        return super().closeEvent(event)

    def handle_playlist_click(self, item):
        self.track_list.load_tracks(item.data(Qt.ItemDataRole.UserRole))
        self.top_bar.toggle_to_tracks(
            item.data(Qt.ItemDataRole.UserRole)['name']
        )
        self.stacked.setCurrentIndex(1)

    def handle_back_button(self):
        self.top_bar.toggle_to_playlists()
        self.stacked.setCurrentIndex(0)

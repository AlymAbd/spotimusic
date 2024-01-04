import requests
from os import path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QHBoxLayout, QSlider, QSplitter, QListWidgetItem, QPushButton
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QPixmap, QIcon
from app import MUSIC_CACHE_PATH, TEMP_PATH, RESOURCE_IMAGE_PATH
from app.workers import WorkerA, WorkerB
from app.models import PlayerSettings
from app.icons import Icons
from app.forms.multilabel import MultiLabelWidget
from app.forms.media_control import MediaControl
from app.forms.current_track import CurrentTrack
from spotipy import Spotify
from app.util import AlbumCover


class Playlist(QWidget):
    media_player = None
    audio_output = None
    client: Spotify = None
    current_volume: int = 50
    player_settings: PlayerSettings = None

    def __init__(self, parent: QWidget | None) -> None:
        from app import client

        super().__init__(parent=parent)

        self.client: Spotify = client.spotify
        self.player_settings = PlayerSettings().get_first().load()
        if self.player_settings.volume:
            self.current_volume = self.player_settings.volume

        self.setMinimumSize(800, 600)
        self.setGeometry(550, 600, 500, 500)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        self.layout = QVBoxLayout()

        self.top_bar = TopPlaylistBar(self)

        media_control_widget = QWidget(self)
        media_control_layout = QHBoxLayout()

        self.media_list = PlaylistList(self)
        self.media_control = MediaControl(media_control_widget)
        self.media_control.setDisabled(True)

        media_control_layout.addWidget(
            self.media_control, alignment=Qt.AlignmentFlag.AlignCenter)

        media_control_widget.setLayout(media_control_layout)

        self.layout.addWidget(self.top_bar)
        self.layout.addWidget(self.media_list)
        self.layout.addWidget(QSplitter())
        self.layout.addWidget(media_control_widget,
                              alignment=Qt.AlignmentFlag.AlignBottom)

        self.media_player.mediaStatusChanged.connect(
            self.media_control.track_control.handle_next_track_behaviour
        )

        self.setLayout(self.layout)

        self.download_worker_a = WorkerA(self)
        self.download_worker_a.update_signal.connect(
            self.media_list.play_selected_music,
        )

        self.download_worker_b = WorkerB(self)
        self.download_worker_b.update_signal.connect(
            self.media_list.update_album_cover)

    def closeEvent(self, event) -> None:
        self.player_settings.set_value('volume', self.current_volume)
        current_track_id = self.media_list.current_music.get('id')
        current_playlist_id = self.media_list.current_playlist.get('id')
        self.player_settings.set_value('last_playlist_id', current_playlist_id)
        self.player_settings.set_value('last_track_id', current_track_id)
        self.player_settings.save()
        return super().closeEvent(event)


class PlaylistList(QWidget):
    client = None
    media_player = None
    current_music = {}
    current_playlist = {}

    offset = 0
    limit = 100

    """
    Playlist, suggestions, albums
    """

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent=parent)

        self.client: Spotify = parent.client
        self.media_player = parent.media_player

        self.layout = QHBoxLayout()

        self.playlist = QListWidget()
        self.playlist.setMinimumSize(250, 100)

        self.current_track_info = CurrentTrack(self)

        self.layout.addWidget(self.playlist)
        self.layout.addWidget(self.current_track_info)

        self.playlist.itemDoubleClicked.connect(self.handle_click)

        self.scrollbar = self.playlist.verticalScrollBar()
        self.scrollbar.valueChanged.connect(self.handle_scrollbar)

        self.setLayout(self.layout)
        self.render_playlists()

    def handle_scrollbar(self, value):
        if value > 0.8 * value:
            value = value

    def update_album_cover(self, track_data):
        """Alias for update_info -> CurrentTrack"""
        self.current_track_info.update_info(track_data)
        current_item = self.playlist.currentItem()
        if current_item:
            multi_label_widget = self.playlist.itemWidget(current_item)
            if isinstance(multi_label_widget, MultiLabelWidget) and not multi_label_widget.album_cover_setted and AlbumCover.cover_exist(track_data['album_id']):
                multi_label_widget.icon_label.setPixmap(
                    QIcon(AlbumCover.get_path(
                        album_id=track_data['album_id'])
                    ).pixmap(40, 40)
                )

    def handle_click(self, item):
        item_data = item.data(Qt.ItemDataRole.UserRole)

        match item_data['type']:
            case 'track':
                self.parent().media_control.setDisabled(False)
                item_data['album_localpath'] = path.join(
                    TEMP_PATH, 'images', item_data['album_id'] + '.jpg')
                if not path.isfile(item_data['album_localpath']):
                    self.download_cover(item_data)
                self.play_selected_music(item_data)
            case 'favorite':
                self.parent().media_control.setDisabled(False)
                self.load_favorite(item_data)
                self.parent().top_bar.button_back.setHidden(False)
            case 'playlist':
                self.parent().media_control.setDisabled(True)
                self.parent().top_bar.button_back.setHidden(False)
                self.load_playlist(item_data)
            case _:
                self.parent().media_control.setDisabled(True)
                self.render_playlists()

    def render_playlists(self):
        self.parent().top_bar.label_main.setText('Playlists')
        result = self.client.current_user_playlists(50, self.offset)
        self.playlist.clear()

        multi_label_widget = MultiLabelWidget(
            big_text=['Favorite'],
            medium_text=[],
            small_text=['Your favorite track'],
            album_id='',
            delimiter=True
        )
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, {
            'id': 0,
            'name': 'Favorite',
            'type': 'favorite'
        })
        item.setSizeHint(multi_label_widget.sizeHint())
        self.playlist.addItem(item)
        self.playlist.setItemWidget(item, multi_label_widget)

        for playlist in result['items']:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, {
                'id': playlist['id'], 'type': 'playlist'
            })

            item.setData(Qt.ItemDataRole.UserRole, {
                'id': playlist['id'],
                'name': playlist['name'],
                'type': 'playlist',
            })

            playlist_image = path.join(
                TEMP_PATH, 'images', playlist['id'] + '.jpg')
            if not path.isfile(playlist_image):
                response = requests.get(playlist['images'][0]['url'])
                if response.status_code == 200:
                    with open(playlist_image, 'wb') as file:
                        file.write(response.content)

            multi_label_widget = MultiLabelWidget(
                big_text=[playlist['name']],
                medium_text=[],
                small_text=[playlist['description']],
                album_id=playlist['id']
            )

            item.setSizeHint(multi_label_widget.sizeHint())
            self.playlist.addItem(item)
            self.playlist.setItemWidget(item, multi_label_widget)

    def load_playlist(self, playlist_data):
        result = self.client.playlist_tracks(
            playlist_data['id'],
            limit=self.limit,
            offset=self.offset,
        )
        self.render_tracks(playlist_data, result)

    def load_favorite(self, data):
        result = self.client.current_user_saved_tracks(
            limit=50,
            offset=self.offset
        )
        self.render_tracks(data, result)

    def render_tracks(self, playlist_data, result):
        self.parent().top_bar.label_main.setText(
            f"Playlist: {playlist_data['name']}")

        self.current_playlist = playlist_data
        self.setWindowTitle(playlist_data['name'])
        self.playlist.clear()
        for track in result['items']:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, {
                'id': track['track']['id'],
                'name': track['track']['name'],
                'type': 'track',
                'album_id': track['track']['album']['id'],
                'album_name': track['track']['album']['name'],
                'album_image_url': track['track']['album']['images'][0]['url'],
                'main_artist_name': track['track']['artists'][0]['name'],
                'artists': [x['name'] for x in track['track']['artists']],
            })
            multi_label_widget = MultiLabelWidget(
                [track['track']['name']],
                [track['track']['artists'][0]['name']],
                [],
                track['track']['album']['id']
            )
            item.setSizeHint(multi_label_widget.sizeHint())
            self.playlist.addItem(item)
            self.playlist.setItemWidget(item, multi_label_widget)

        self.parent().top_bar.label_main.setText(
            f'Music List ({self.playlist.count()})')

    def play_selected_music(self, track_data):
        self.current_track_info.update_info(track_data, 1)
        self.parent().media_control.track_control.media_stop()

        self.playlist.setDisabled(True)
        self.update_album_cover(track_data)
        self.current_music = track_data

        self.setWindowTitle(
            self.current_playlist['name'] + ': ' + self.current_music['name'])
        file_path = path.join(MUSIC_CACHE_PATH, track_data['id'] + '.mp3')

        if not path.isfile(file_path):
            self.parent().download_worker_a.set_data('play_track', track_data)
            self.parent().download_worker_a.start()
            return

        self.current_track_info.update_info(track_data)
        self.playlist.setDisabled(False)
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.parent().media_control.track_control.media_playpause(True)

    def download_cover(self, track_data):
        self.parent().download_worker_b.set_data('update_cover', track_data)
        self.parent().download_worker_b.start()


class TopPlaylistBar(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.layout = QHBoxLayout()

        self.label_main = QLabel('Playlists')
        self.button_back = QPushButton()
        self.button_back.setToolTip('Back to previous page')
        self.button_back.setIcon(
            QIcon(Icons('direction.arrow-left-circle').str))
        self.button_back.setMaximumWidth(40)
        self.button_back.clicked.connect(self.handle_back_button)
        self.button_back.setHidden(True)

        self.layout.addWidget(
            self.button_back, alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.layout.addWidget(
            self.label_main, alignment=Qt.AlignmentFlag.AlignLeft
        )

        self.setLayout(self.layout)

    def handle_back_button(self):
        self.parent().media_list.render_playlists()
        self.button_back.setHidden(True)

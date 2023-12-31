import requests
from os import path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QHBoxLayout, QSlider, QSplitter, QListWidgetItem, QPushButton
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QPixmap, QIcon
from app import MUSIC_CACHE_PATH, TEMP_PATH, RESOURCE_IMAGE_PATH
from app.workers import WorkerA
from app.models import PlayerSettings
from app.icons import Icons
from app.forms.multilabel import MultiLabelWidget
from app.forms.media_control import MediaControl, TrackControl, AudioControl


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

        self.layout.addWidget(
            self.button_back, alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.layout.addWidget(
            self.label_main, alignment=Qt.AlignmentFlag.AlignLeft
        )

        self.setLayout(self.layout)

    def handle_back_button(self):
        self.parent().media_list.render_playlists()


class Playlist(QWidget):
    media_player = None
    audio_output = None
    client = None
    current_volume: int = 50
    player_settings: PlayerSettings = None

    def __init__(self, parent: QWidget | None) -> None:
        from app.client import client

        super().__init__(parent=parent)

        self.client = client
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
        self.media_control = MediaControl(media_control_widget)
        self.track_control = TrackControl(media_control_widget)

        self.slider_volume = QSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setMinimumSize(50, 20)
        self.slider_volume.setMaximumSize(150, 20)
        self.slider_volume.valueChanged.connect(self.change_volume)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(self.current_volume)

        media_control_layout.addWidget(self.slider_volume)
        media_control_layout.addWidget(
            self.media_control, alignment=Qt.AlignmentFlag.AlignCenter)
        media_control_layout.addWidget(
            self.track_control, alignment=Qt.AlignmentFlag.AlignRight)

        media_control_widget.setLayout(media_control_layout)

        self.media_list = PlaylistList(self)
        self.audio_control = AudioControl(self)

        self.label_current_track = QLabel('...')

        self.layout.addWidget(self.top_bar)
        self.layout.addWidget(self.media_list)
        self.layout.addWidget(QSplitter())
        self.layout.addWidget(self.label_current_track,
                              alignment=Qt.AlignmentFlag.AlignBottom)
        self.layout.addWidget(media_control_widget,
                              alignment=Qt.AlignmentFlag.AlignBottom)
        self.layout.addWidget(self.audio_control,
                              alignment=Qt.AlignmentFlag.AlignBottom)

        self.setLayout(self.layout)

    def change_volume(self, value):
        self.audio_output.setVolume(float(value/100))
        self.current_volume = value

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

    """
    Playlist, suggestions, albums
    """

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent=parent)

        self.client = parent.client
        self.media_player = parent.media_player

        self.layout = QHBoxLayout()

        self.playlist = QListWidget()
        self.playlist.setMinimumSize(250, 100)

        self.album_cover = QLabel()
        self.album_cover.setMaximumSize(200, 200)

        self.layout.addWidget(self.playlist)
        self.layout.addWidget(self.album_cover)
        self.setLayout(self.layout)
        self.render_playlists()
        self.playlist.itemDoubleClicked.connect(self.handle_click)

    def update_album_cover(self, track_data):
        file_path = track_data['album_localpath'] if path.isfile(
            track_data['album_localpath']) else path.join(RESOURCE_IMAGE_PATH, 'default_image_cover.jpeg')
        picture = QPixmap(file_path)
        picture = picture.scaled(
            200, 200, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        self.album_cover.setPixmap(picture)

    def handle_click(self, item):
        item_data = item.data(Qt.ItemDataRole.UserRole)

        match item_data['type']:
            case 'track':
                item_data['album_localpath'] = path.join(
                    TEMP_PATH, 'images', item_data['album_id'] + '.jpg')
                if not path.isfile(item_data['album_localpath']):
                    self.download_cover(item_data)
                self.play_selected_music(item_data)
            case 'playlist':
                self.load_playlist(item_data)
            case _:
                self.render_playlists()

    def render_playlists(self):
        self.parent().top_bar.label_main.setText('Playlists')
        result = self.client.current_user_playlists()
        self.playlist.clear()
        for playlist in result['items']:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, {
                         'id': playlist['id'], 'type': 'playlist'})

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
        self.parent().top_bar.label_main.setText(
            f"Playlist: {playlist_data['name']}")

        self.current_playlist = playlist_data
        self.setWindowTitle(playlist_data['name'])
        result = self.client.playlist_tracks(playlist_data['id'])
        self.playlist.clear()
        for track in result['items']:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, {
                'id': track['track']['id'],
                'type': 'track',
                'album_id': track['track']['album']['id'],
                'album_image_url': track['track']['album']['images'][0]['url'],
                'main_artist_name': track['track']['artists'][0]['name'],
                'name': track['track']['name']
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

        self.parent().label_current_track.setText(
            f'Music List ({self.playlist.count()})')

    def play_selected_music(self, track_data):
        self.update_music_label(track_data, 1)
        self.parent().media_control.media_stop()
        self.playlist.setDisabled(True)
        self.update_album_cover(track_data)
        self.current_music = track_data
        self.setWindowTitle(
            self.current_playlist['name'] + ': ' + self.current_music['name'])
        file_path = path.join(MUSIC_CACHE_PATH, track_data['id'] + '.mp3')

        if not path.isfile(file_path):
            self.download_worker = WorkerA('play_track', kwargs=track_data)
            self.download_worker.update_signal.connect(
                self.play_selected_music)
            self.download_worker.start()
            return

        self.update_music_label(track_data)
        self.playlist.setDisabled(False)
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.parent().media_control.media_playpause(True)

    def update_music_label(self, track_data, percentage=None):
        title = track_data['name']
        if percentage and percentage >= 0:
            title = f" *caching* {title}"
        self.parent().label_current_track.setText(title)

    def download_cover(self, track_data):
        self.download_worker = WorkerA('update_cover', kwargs=track_data)
        self.download_worker.update_signal.connect(self.update_album_cover)
        self.download_worker.start()

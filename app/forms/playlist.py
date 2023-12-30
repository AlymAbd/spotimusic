from os import path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel, QHBoxLayout, QSlider, QSplitter, QListWidgetItem, QStyle, QGridLayout, QSizePolicy
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QCloseEvent, QIcon, QPixmap
from app import MUSIC_CACHE_PATH, TEMP_PATH, RESOURCE_IMAGE_PATH
from app.workers import WorkerA
from app.models import PlayerSettings
from app.icons import Icons
import requests


class MultiLabelWidget(QWidget):
    def __init__(self, big_text: list = [], medium_text: list = [], small_text: list = [], album_id: str = None):
        super().__init__()

        hlayout = QHBoxLayout(self)
        self.track_info = TrackInfoWidget(self, big_text, medium_text, small_text)
        hlayout.addWidget(self.track_info)

        if album_id:
            icon_path = path.join(TEMP_PATH, 'images', path.join(album_id) + '.jpg') if path.isfile(path.join(TEMP_PATH, 'images', path.join(album_id) + '.jpg')) else path.join(RESOURCE_IMAGE_PATH, 'default_image_cover.jpeg')
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(icon_path).pixmap(40, 40))  # Adjust the size as needed
            hlayout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignRight)

class TrackInfoWidget(QWidget):
    def __init__(self, parent, big_text: list = [], medium_text: list = [], small_text: list = []):
        super().__init__()
        font_size_factor = 1.04
        vlayout = QVBoxLayout(self)

        for text in big_text:
            label = QLabel(text)
            font = label.font()
            font.setPointSizeF(font.pointSizeF() * font_size_factor)
            label.setFont(font)
            label.setWordWrap(True)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            vlayout.addWidget(label)

        for text in medium_text:
            label = QLabel(text)
            font = label.font()
            font.setPointSizeF(font.pointSizeF() * font_size_factor)
            font.setUnderline(True)
            label.setWordWrap(True)
            label.setFont(font)
            vlayout.addWidget(label)

        for text in small_text:
            label = QLabel(text)
            font = label.font()
            font.setPointSizeF(font.pointSizeF() * 0.9)
            label.setWordWrap(True)
            label.setFont(font)
            vlayout.addWidget(label)


class Playlist(QWidget):
    media_player = None
    audio_output = None
    client = None
    current_volume: int = 50
    player_settings: PlayerSettings = None

    def __init__(self, parent: QWidget | None) -> None:
        from app.client import client
        self.client = client
        self.player_settings = PlayerSettings().get_first().load()
        if self.player_settings.volume:
            self.current_volume = self.player_settings.volume

        super().__init__(parent = parent)
        self.setMinimumSize(800, 600)
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
        self.slider_volume.setValue(self.current_volume)

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
    current_playlist = {}

    """
    Playlist, suggestions, albums
    """
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent = parent)

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
        self.render_playlist()
        self.playlist.itemDoubleClicked.connect(self.handle_click)

    def update_album_cover(self, track_data):
        file_path = track_data['album_localpath'] if path.isfile(track_data['album_localpath']) else path.join(RESOURCE_IMAGE_PATH, 'default_image_cover.jpeg')
        picture = QPixmap(file_path)
        picture = picture.scaled(200, 200, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        self.album_cover.setPixmap(picture)

    def handle_click(self, item):
        item_data = item.data(Qt.ItemDataRole.UserRole)

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
            item.setData(Qt.ItemDataRole.UserRole, {'id': playlist['id'], 'type': 'playlist'})

            item.setData(Qt.ItemDataRole.UserRole, {
                'id': playlist['id'],
                'name': playlist['name'],
                'type': 'playlist',
            })

            playlist_image = path.join(TEMP_PATH, 'images', playlist['id'] + '.jpg')
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

        self.parent().label_current_track.setText(f'Music List ({self.playlist.count()})')

    def play_selected_music(self, track_data):
        self.update_music_label(track_data, 1)
        self.parent().media_control.media_stop()
        self.playlist.setDisabled(True)
        self.update_album_cover(track_data)
        self.current_music = track_data
        self.setWindowTitle(self.current_playlist['name'] + ': ' + self.current_music['name'])
        file_path = path.join(MUSIC_CACHE_PATH, track_data['id'] + '.mp3')

        if not path.isfile(file_path):
            self.download_worker = WorkerA('play_track', kwargs=track_data)
            self.download_worker.update_signal.connect(self.play_selected_music)
            self.download_worker.start()
            return

        self.update_music_label(track_data)
        self.playlist.setDisabled(False)
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.parent().media_control.media_playpause(True)

    def update_music_label(self, track_data, percentage = None):
        title = track_data['name']
        if percentage and percentage >= 0:
            title = f" *caching* {title}"
        self.parent().label_current_track.setText(title)

    def download_cover(self, track_data):
        self.download_worker = WorkerA('update_cover', kwargs=track_data)
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
        self.button_next.setToolTip('Next track')
        self.button_next.setIcon(QIcon(Icons('media.forward').str))
        self.button_next.setMaximumSize(50, 50)
        self.button_next.setMinimumSize(30, 30)
        self.button_next.clicked.connect(self.media_next)

        self.button_prev = QPushButton()
        self.button_prev.setToolTip('Previous track')
        self.button_prev.setIcon(QIcon(Icons('media.backward').str))
        self.button_prev.setMaximumSize(50, 50)
        self.button_prev.setMinimumSize(30, 30)
        self.button_prev.clicked.connect(self.media_prev)

        self.button_play_pause = QPushButton()
        self.button_play_pause.setToolTip('Play-pause')
        self.button_play_pause.setIcon(QIcon(Icons('media.play').str))
        self.button_play_pause.setMaximumSize(60, 60)
        self.button_play_pause.setMinimumSize(35, 35)
        self.button_play_pause.setCheckable(True)
        self.button_play_pause.clicked.connect(self.media_playpause)

        self.button_stop = QPushButton()
        self.button_stop.setToolTip('Stop track')
        self.button_stop.setIcon(QIcon(Icons('media.stop').str))
        self.button_stop.setMaximumSize(60, 60)
        self.button_stop.setMinimumSize(35, 35)
        self.button_stop.clicked.connect(self.media_stop)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_current_seek_position)
        self.timer.start(500)

        self.layout.addWidget(self.button_prev)
        self.layout.addWidget(self.button_stop)
        self.layout.addWidget(self.button_play_pause)
        self.layout.addWidget(self.button_next)

        self.setLayout(self.layout)

    def media_stop(self):
        self.grandparent.media_player.stop()
        self.grandparent.label_current_track.setText('')

    def media_playpause(self, value):
        if not self.grandparent.media_player.isPlaying():
            self.button_play_pause.setIcon(QIcon(Icons('media.pause').str))
            self.grandparent.media_player.play()
            self.button_play_pause.setChecked(True)
            self.update_current_seek_position()
        else:
            self.button_play_pause.setIcon(QIcon(Icons('media.play').str))
            self.grandparent.media_player.pause()
            self.button_play_pause.setChecked(False)

    def media_next(self):
        current_index = self.grandparent.media_list.playlist.indexFromItem(self.grandparent.media_list.playlist.currentItem()).row()
        next_index = current_index + 1
        if (next_index + 1) > self.grandparent.media_list.playlist.count():
            next_index = 0
        self._change_track(next_index)

    def media_prev(self):
        current_index = self.grandparent.media_list.playlist.indexFromItem(self.grandparent.media_list.playlist.currentItem()).row()
        next_index = current_index - 1
        if (next_index < 0):
            next_index = self.grandparent.media_list.playlist.count() - 1
        self._change_track(next_index)

    def _change_track(self, index):
        self.grandparent.media_player.stop()
        next_item = self.grandparent.media_list.playlist.item(index)
        next_item.setSelected(True)
        self.grandparent.media_list.playlist.setCurrentItem(next_item)
        self.grandparent.media_list.handle_click(next_item)

    def update_current_seek_position(self):
        position = self.grandparent.media_player.position()
        self.grandparent.audio_control.slider_position.setValue(position)
        self.grandparent.audio_control.label.setText(f'{self.format_time(position)} / {self.format_time(self.grandparent.media_player.duration())}')

    def format_time(self, milliseconds):
        minutes, seconds = divmod(milliseconds // 1000, 60)
        return f'{minutes:02d}:{seconds:02d}'

class TrackControl(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent = parent)

        self.layout = QHBoxLayout()

        self.button_add = QPushButton()
        self.button_add.setIcon(QIcon(Icons('interface.heart').str))
        self.button_add.setToolTip('Add to favorite')
        self.button_add.setMaximumSize(30, 30)

        self.button_similar = QPushButton()
        self.button_similar.setIcon(QIcon(Icons('interface.infinite').str))
        self.button_similar.setToolTip('Add to favorite')
        self.button_similar.setMaximumSize(30, 30)

        self.button_shuffle = QPushButton()
        self.button_shuffle.setIcon(QIcon(Icons('media.shuffle').str))
        self.button_shuffle.setToolTip('Shuffle playlist')
        self.button_shuffle.setMaximumSize(30, 30)

        self.button_mute = QPushButton()
        self.button_mute.setToolTip('Mute')
        self.button_mute.setIcon(QIcon(Icons('media.volume-mute').str))
        self.button_mute.setMaximumSize(30, 30)

        self.button_download_all = QPushButton()
        self.button_download_all.setToolTip('Download all')
        self.button_download_all.setIcon(QIcon(Icons('web.download').str))
        self.button_download_all.setMaximumSize(30, 30)

        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.setMinimumWidth(10)

        self.layout.addWidget(self.button_add)
        self.layout.addWidget(self.button_similar)
        self.layout.addWidget(splitter)
        self.layout.addWidget(self.button_shuffle)
        self.layout.addWidget(self.button_mute)
        self.layout.addWidget(splitter)
        self.layout.addWidget(self.button_download_all)

        self.setLayout(self.layout)

class AudioControl(QWidget):
    """
    Track position, track info
    """
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent = parent)
        self.layout = QHBoxLayout()
        self.label = QLabel('00:00 | 00:00')
        self.slider_position = QSlider(Qt.Orientation.Horizontal)
        self.slider_position.setMinimumSize(100, 10)
        self.slider_position.setMaximum(100)
        self.slider_position.setMinimum(0)
        self.slider_position.sliderMoved.connect(self.slider_position_moved)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.slider_position)
        self.setLayout(self.layout)

    def slider_position_moved(self, value):
        duration = self.parent().media_player.duration()
        new_position = value * duration / self.slider_position.maximum()
        self.parent().media_player.setPosition(int(new_position))

from .base import BaseLayout

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel, QHBoxLayout, QSlider, QSplitter, QListWidgetItem
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon
from pytube import YouTube, Search


class Playlist(QWidget):
    playlist_loaded: bool = True
    music_in_progress: bool = True

    def __init__(self, parent: QWidget) -> None:
        from app.client import client
        self.client = client

        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def translate(self):
        return super().translate()

    def setup_ui(self):
        self.setWindowTitle('Playlist')
        self.setGeometry(600, 600, 600, 600)

        self.container = QWidget(self)
        self.layout = QVBoxLayout(self)
        self.audio_control = AudioControl(self)
        self.media_control = MediaControl(self)

        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.playlist = QListWidget()

        self.label_main = QLabel('Music list:')

        self.button_back = QPushButton('Back')
        self.button_back.clicked.connect(self.load_playlists)
        self.button_back.setVisible(False)

        self.label_current_music = QLabel('... ... ...')
        self.layout_music_info = QHBoxLayout()
        self.layout_music_info.addWidget(self.label_current_music)

        splitter = QSplitter()

        self.layout.addWidget(self.label_main)
        self.layout.addLayout(self.layout_music_info, 100)
        self.audio_control.set_ui()
        self.layout.addWidget(splitter)
        self.media_control.set_ui()
        self.container.setLayout(self.layout)

    def load_playlists(self):
        pass



class Playlists(BaseLayout):
    path: str = 'tmp'
    playlist_loaded: bool = True
    music_in_progress: bool = True
    current_music = True

    def translate(self):
        return super().translate()

    def setup_ui(self):
        layout = QVBoxLayout(self.parent)
        container = QWidget(self.parent)

        self.parent.setWindowTitle('Playlist')
        # self.parent.setGeometry(600, 600, 600, 600)

        # Create media player and playlist
        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.playlist = QListWidget()

        layout_button_row = QHBoxLayout()
        layout_music_bar = QHBoxLayout()

        # layout_music_info_layout = QHBoxLayout()
        # self.current_music_label = QLabel('')
        # layout_music_info_layout.addWidget(self.current_music_label)

        # Create widgets
        # self.back_playlist_button = QPushButton("Back")
        # self.back_playlist_button.clicked.connect(self.load_playlists)
        # self.back_playlist_button.setVisible(False)

        # self.button_play_pause = QPushButton(QIcon.fromTheme('media-playback-start'), '')
        # self.button_play_pause.clicked.connect(self.pause_play_music)

        # self.stop_button = QPushButton(QIcon.fromTheme('media-playback-stop'), '')
        # self.stop_button.clicked.connect(self.stop_music)

        # self.button_next_track = QPushButton(QIcon.fromTheme('media-skip-forward'), '')
        # self.button_next_track.clicked.connect(self.next_track)

        # self.button_prev_track = QPushButton(QIcon.fromTheme('media-skip-backward'), '')
        # self.button_prev_track.clicked.connect(self.previous_track)

        # volume_label = QLabel('Volume:')
        # self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        # self.volume_slider.setRange(0, 100)
        # self.volume_slider.setValue(50)
        # self.volume_slider.setMinimumWidth(40)
        # self.volume_slider.setMaximumWidth(70)
        # self.volume_slider.valueChanged.connect(self.set_volume)

        # self.position_slider = QSlider(Qt.Orientation.Horizontal)
        # self.position_slider.setMinimum(0)
        # self.position_slider.setMaximum(100)
        # self.position_slider.setValue(0)
        # self.position_slider.sliderMoved.connect(self.slider_moved)

        # self.position_slider_label = QLabel('0:00')
        # self.current_music_label = QLabel('')
        splitter = QSplitter()

        # layout_button_row.addWidget(volume_label)
        # layout_button_row.addWidget(self.volume_slider)
        # layout_button_row.addWidget(self.position_slider_label)
        # layout_button_row.addWidget(self.position_slider)

        # layout_music_bar.addWidget(splitter)
        # layout_music_bar.addWidget(self.button_prev_track)
        # layout_music_bar.addWidget(self.button_play_pause)
        # layout_music_bar.addWidget(self.stop_button)
        # layout_music_bar.addWidget(self.button_next_track)

        self.music_list_label = QLabel('Music List:')
        self.music_list = QListWidget()
        self.load_playlists()  # Replace with your folder path
        self.music_list.itemDoubleClicked.connect(self.load_playlists)

        # Layout
        layout.addWidget(splitter)
        layout.addWidget(self.back_playlist_button)
        layout.addWidget(self.music_list_label)
        layout.addWidget(self.music_list)

        # layout.addLayout(layout_music_info_layout)
        # layout.addLayout(layout_music_bar)
        # layout.addLayout(layout_button_row)

        self.audio_control = AudioControl(self)

        container.setLayout(layout)

        # Set window properties
        self.parent.setWindowTitle('Music Player')
        self.parent.setGeometry(100, 100, 400, 400)

    def load_playlists(self, current_item = None):
        self.music_in_progress = False
        if current_item and self.playlist_loaded:
            # load tracklist
            self.back_playlist_button.setVisible(True)
            self.playlist_loaded = False
            playlist_name = current_item.text()
            playlist_id = current_item.data(Qt.ItemDataRole.UserRole)['id']
            self.setWindowTitle(playlist_name)
            self.music_list.clear()
            results = client.playlist_tracks(playlist_id)
            for track in results['items']:
                item = QListWidgetItem()
                item.setText(f"{track['track']['artists'][0]['name']}: {track['track']['name']}")
                item.setData(Qt.ItemDataRole.UserRole, {'id': track['track']['id']})
                self.music_list.addItem(item)
            self.music_list_label.setText(f'Music List ({self.music_list.count()})')
        elif current_item and not self.playlist_loaded:
            # play music
            self.play_selected_music(current_item)
        else:
            # load playlist
            self.music_list.clear()
            self.back_playlist_button.setVisible(False)
            self.playlist_loaded = True
            results = client.current_user_playlists()
            for playlist in results['items']:
                item = QListWidgetItem()
                item.setText(playlist['name'])
                item.setData(Qt.ItemDataRole.UserRole, {'id': playlist['id']})
                self.music_list.addItem(item)
            self.music_list_label.setText(f'Music List ({self.music_list.count()})')

    def play_selected_music(self, item):
        self.stop_music()
        self.current_music = item
        music_name = item.text()
        item_data = item.data(Qt.ItemDataRole.UserRole)
        music_id = item_data['id']
        self.setWindowTitle(music_name)
        fullpath = os.path.join(os.getcwd(), self.path, music_id+'.mp3')
        self.current_music_label.setText(f'(*caching*) {self.current_music_label}')

        if not os.path.isfile(fullpath):
            search = Search(music_name)
            results = search.results
            result = results[0].watch_url
            stream = YouTube(result)
            stream = stream.streams.filter(only_audio=True).first()
            stream.download(self.path, music_id+'.mp3')

        audio = QAudioOutput()
        self.media_player.setAudioOutput(audio)
        self.media_player.setSource(QUrl.fromLocalFile(fullpath))
        self.media_player.play()
        self.current_music_label.setText(music_name)
        self.music_in_progress = True
        self.button_play_pause.setIcon(QIcon.fromTheme('media-playback-pause'))

    def pause_play_music(self) -> None:
        if self.music_in_progress:
            self.button_play_pause.setIcon(QIcon.fromTheme('media-playback-start'))
            self.music_in_progress = False
            self.media_player.pause()
        elif self.playlist_loaded:
            pass
        else:
            self.media_player.play()
            self.button_play_pause.setIcon(QIcon.fromTheme('media-playback-pause'))
            self.music_in_progress = True

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

    def set_volume(self, value):
        self.media_player
        self.media_player.setVolume(value)

    def slider_moved(self, value):
        self.position_slider_label.setText(str(value))


class MediaControl(BaseLayout):
    def translate(self):
        return super().translate()

    def setup_ui(self):
        self.layout_button_row = QHBoxLayout()

        self.button_play_pause = QPushButton('Play')
        self.button_play_pause.setIcon(QIcon.fromTheme('media-playback-start'))
        self.button_play_pause.clicked.connect(self.click_playpause)
        self.button_play_pause.setCheckable(True)

        self.button_stop_track = QPushButton('Stop')
        self.button_stop_track.setIcon(QIcon.fromTheme('media-playback-stop'))
        self.button_stop_track.clicked.connect(self.click_stop)

        self.button_next_track = QPushButton('Next-track')
        self.button_next_track.setIcon(QIcon.fromTheme('media-playback-forward'))
        self.button_next_track.clicked.connect(self.click_next)

        self.button_prev_track = QPushButton('Prev-track')
        self.button_prev_track.setIcon(QIcon.fromTheme('media-playback-backward'))
        self.button_prev_track.clicked.connect(self.click_prev)

        self.layout_button_row.addWidget(self.button_prev_track)
        self.layout_button_row.addWidget(self.button_play_pause)
        self.layout_button_row.addWidget(self.button_stop_track)
        self.layout_button_row.addWidget(self.button_next_track)

        self.parent.layout.addLayout(self.layout_button_row)

    def click_playpause(self):
        pass

    def click_stop(self):
        pass

    def click_next(self):
        pass

    def click_prev(self):
        pass


class AudioControl(BaseLayout):
    def translate(self):
        return super().translate()

    def setup_ui(self):
        self.layout_button_row = QHBoxLayout()

        label_volume = QLabel('Volume:')
        self.slider_volume = QSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(50)
        self.slider_volume.setMinimumWidth(50)
        self.slider_volume.setMaximumWidth(80)
        self.slider_volume.valueChanged.connect(self.onchange_volume)

        self.slider_position = QSlider(Qt.Orientation.Horizontal)
        self.slider_position.setMinimum(0)
        self.slider_position.setMaximum(100)
        self.slider_position.setValue(0)
        self.slider_position.sliderMoved.connect(self.onchange_position)

        self.label_position = QLabel('0:00')

        self.layout_button_row.addWidget(label_volume)
        self.layout_button_row.addWidget(self.slider_volume)
        self.layout_button_row.addWidget(self.slider_position)

        self.parent.layout.addLayout(self.layout_button_row)

    def onchange_volume(self, value):
        pass

    def onchange_position(self, value):
        pass



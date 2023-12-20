import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QSlider, QLabel
from PyQt5.QtWidgets import QWidget, QListWidget, QListWidgetItem, QDesktopWidget, QHBoxLayout, QSplitter
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtCore import Qt, QUrl
from client import client
from pytube import YouTube, Search

sp = client()

class MusicPlayer(QMainWindow):
    path: str = 'tmp'
    playlist_loaded: bool = True
    music_in_progress: bool = True
    current_music = True

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(500)
        self.setMinimumWidth(700)

        self.init_ui()
        self.center_window()

    def init_ui(self):
        # Create media player and playlist
        self.media_player = QMediaPlayer()
        self.playlist = QMediaPlaylist(self.media_player)
        self.media_player.setPlaylist(self.playlist)

        button_row_layout = QHBoxLayout()
        music_bar_layout = QHBoxLayout()
        music_info_layout = QHBoxLayout()

        # Create widgets
        self.back_playlist_button = QPushButton("Back")
        self.back_playlist_button.clicked.connect(self.load_playlists)
        self.back_playlist_button.setVisible(False)

        self.button_play_pause = QPushButton(QIcon.fromTheme('media-playback-start'), '')
        self.button_play_pause.clicked.connect(self.pause_play_music)

        self.stop_button = QPushButton(QIcon.fromTheme('media-playback-stop'), '')
        self.stop_button.clicked.connect(self.stop_music)

        self.button_next_track = QPushButton(QIcon.fromTheme('media-skip-forward'), '')
        self.button_next_track.clicked.connect(self.next_track)

        self.button_prev_track = QPushButton(QIcon.fromTheme('media-skip-backward'), '')
        self.button_prev_track.clicked.connect(self.previous_track)

        volume_label = QLabel('Volume:')
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setMinimumWidth(40)
        self.volume_slider.setMaximumWidth(70)
        self.volume_slider.valueChanged.connect(self.set_volume)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setMinimum(0)
        self.position_slider.setMaximum(100)
        self.position_slider.setValue(0)
        self.position_slider.sliderMoved.connect(self.slider_moved)

        self.position_slider_label = QLabel('0:00')
        self.current_music_label = QLabel('')
        splitter = QSplitter()

        button_row_layout.addWidget(volume_label)
        button_row_layout.addWidget(self.volume_slider)
        button_row_layout.addWidget(self.position_slider_label)
        button_row_layout.addWidget(self.position_slider)
        music_info_layout.addWidget(self.current_music_label)
        # music_bar_layout.addWidget(splitter)
        music_bar_layout.addWidget(self.button_prev_track)
        music_bar_layout.addWidget(self.button_play_pause)
        music_bar_layout.addWidget(self.stop_button)
        music_bar_layout.addWidget(self.button_next_track)

        self.music_list_label = QLabel('Music List:')
        self.music_list = QListWidget()
        self.load_playlists()  # Replace with your folder path
        self.music_list.itemDoubleClicked.connect(self.load_playlists)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        layout.addWidget(self.back_playlist_button)
        layout.addWidget(self.music_list_label)
        layout.addWidget(self.music_list)

        layout.addLayout(music_info_layout)
        layout.addLayout(music_bar_layout)
        layout.addLayout(button_row_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Set window properties
        self.setWindowTitle('Music Player')
        self.setGeometry(100, 100, 400, 400)

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
            results = sp.playlist_tracks(playlist_id)
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
            results = sp.current_user_playlists()
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

        media = QMediaContent(QUrl.fromLocalFile(fullpath))
        self.media_player.setMedia(media)
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
        self.media_player.setVolume(value)

    def center_window(self):
        self.setWindowTitle("Spotify App")

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def slider_moved(self, value):
        self.position_slider_label.setText(str(value))

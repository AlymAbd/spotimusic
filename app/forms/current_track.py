from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QHBoxLayout, QSlider, QSplitter, QListWidgetItem, QPushButton
from os import path
from app import MUSIC_CACHE_PATH, TEMP_PATH, RESOURCE_IMAGE_PATH
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QUrl, Qt


class CurrentTrack(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.layout = QVBoxLayout()

        self.label_current_artist = QLabel()
        self.label_current_track = QLabel()
        self.label_current_album = QLabel()

        self.album_cover = QLabel()
        self.album_cover.setMaximumSize(200, 200)

        self.layout.addWidget(self.album_cover)
        self.layout.addWidget(self.label_current_artist)
        self.layout.addWidget(self.label_current_album)
        self.layout.addWidget(self.label_current_track)

        self.setLayout(self.layout)

    def update_info(self, track_data):
        self.label_current_album.setText(track_data.get(''))
        self.label_current_artist.setText(track_data.get(''))
        self.label_current_track.setText(track_data.get(''))

        file_path = track_data['album_localpath'] if path.isfile(
            track_data['album_localpath']) else path.join(RESOURCE_IMAGE_PATH, 'default_image_cover.jpeg')
        picture = QPixmap(file_path)
        picture = picture.scaled(
            200, 200, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        self.album_cover.setPixmap(picture)

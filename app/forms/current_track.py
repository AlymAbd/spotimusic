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
        self.layout.addWidget(self.label_current_track)
        self.layout.addWidget(self.label_current_album)
        self.layout.addWidget(self.label_current_artist)

        self.setLayout(self.layout)

    def update_info(self, track_data, percentage=None):
        self.label_current_album.setText(
            f"Album name: {track_data.get('album_name')}"
        )
        self.label_current_artist.setText(
            f"Artists: {', '.join(track_data.get('artists', []))}"
        )

        if percentage and percentage >= 0:
            self.label_current_track.setText(
                f" *caching* {track_data.get('name')}")
        else:
            self.label_current_track.setText(
                f"Title: {track_data.get('name')}"
            )

        if track_data.get('album_localpath'):
            file_path = track_data['album_localpath'] if path.isfile(
                track_data['album_localpath']) else path.join(RESOURCE_IMAGE_PATH, 'default_image_cover.jpeg')
            picture = QPixmap(file_path)
            picture = picture.scaled(
                200, 200, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
            self.album_cover.setPixmap(picture)

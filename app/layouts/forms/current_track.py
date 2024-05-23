from os import path
from app import RESOURCE_IMAGE_PATH
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class CurrentTrack(QWidget):
    track_list = None

    def __init__(self, parent):
        super().__init__()

        self.track_list = parent
        self.layout = QVBoxLayout()

        self.label_current_artist = QLabel()
        self.label_current_track = QLabel()
        self.label_current_album = QLabel()

        self.label_current_artist.setWordWrap(True)
        self.label_current_track.setWordWrap(True)
        self.label_current_album.setWordWrap(True)

        self.album_cover = QLabel()
        self.album_cover.setMaximumSize(200, 200)

        label_widget = QWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(self.label_current_track)
        layout.addWidget(self.label_current_album)
        layout.addWidget(self.label_current_artist)
        label_widget.setLayout(layout)

        self.layout.addWidget(self.album_cover)
        self.layout.addWidget(label_widget)
        self.setLayout(self.layout)

    def update_info(self, track_data, caching=None):
        self.label_current_album.setText(
            f"Album: {track_data.get('album_name')}"
        )
        self.label_current_artist.setText(
            f"Artists: {', '.join(track_data.get('artists', []))}"
        )

        if caching:
            self.track_list.media_list.status_bar.showMessage(
                f"*caching* {track_data.get('name')}")
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

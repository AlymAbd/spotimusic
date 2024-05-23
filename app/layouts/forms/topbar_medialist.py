from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from app.core.utils import Icons


class TopPlaylistBar(QWidget):
    label_main = None
    button_back = None

    def __init__(self, parent: QWidget):
        super().__init__()
        layout = QHBoxLayout()

        self.label_main = QLabel('Playlists')
        self.button_back = QPushButton()
        self.button_back.setToolTip('Back to previous page')
        self.button_back.setIcon(
            QIcon(Icons('direction.arrow-left-circle').str))
        self.button_back.setMaximumWidth(40)
        self.button_back.setHidden(True)

        layout.addWidget(
            self.button_back, alignment=Qt.AlignmentFlag.AlignLeft
        )
        layout.addWidget(
            self.label_main, alignment=Qt.AlignmentFlag.AlignLeft
        )

        self.setLayout(layout)

    def toggle_to_playlists(self):
        self.button_back.setHidden(True)
        self.label_main.setText('Playlists')

    def toggle_to_tracks(self, playlist_name):
        self.button_back.setHidden(False)
        self.label_main.setText(playlist_name)

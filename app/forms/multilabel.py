from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from app.forms.other import DelimiterItemWidget
from app.util import AlbumCover


class MultiLabelWidget(QWidget):
    album_cover_setted: bool = False

    def __init__(
        self,
        big_text: list = [],
        medium_text: list = [],
        small_text: list = [],
        album_id: str = None,
        delimiter: bool = False
    ):
        super().__init__()

        hlayout = QHBoxLayout(self)
        self.track_info = TrackInfoWidget(
            self, big_text, medium_text, small_text)
        hlayout.addWidget(self.track_info)

        if album_id is not None:
            self.album_cover_setted = AlbumCover.cover_exist(album_id=album_id)
            icon_path = AlbumCover.get_path(album_id, True)
            self.icon_label = QLabel()
            self.icon_label.setPixmap(QIcon(icon_path).pixmap(40, 40))
            hlayout.addWidget(
                self.icon_label, alignment=Qt.AlignmentFlag.AlignRight)

        if delimiter:
            hlayout.addWidget(DelimiterItemWidget())

        self.setLayout(hlayout)


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
            label.setSizePolicy(QSizePolicy.Policy.Expanding,
                                QSizePolicy.Policy.Preferred)
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

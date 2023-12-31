from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QSlider, QSplitter
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from app.icons import Icons


class MediaControl(QWidget):
    grandparent: QWidget = None

    """
    Buttons next, prev, play, pause, stop, add/remove to favorite
    """

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent=parent)
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
        current_index = self.grandparent.media_list.playlist.indexFromItem(
            self.grandparent.media_list.playlist.currentItem()).row()
        next_index = current_index + 1
        if (next_index + 1) > self.grandparent.media_list.playlist.count():
            next_index = 0
        self._change_track(next_index)

    def media_prev(self):
        current_index = self.grandparent.media_list.playlist.indexFromItem(
            self.grandparent.media_list.playlist.currentItem()).row()
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
        self.grandparent.audio_control.label.setText(
            f'{self.format_time(position)} / {self.format_time(self.grandparent.media_player.duration())}')

    def format_time(self, milliseconds):
        minutes, seconds = divmod(milliseconds // 1000, 60)
        return f'{minutes:02d}:{seconds:02d}'


class TrackControl(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent=parent)

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
        super().__init__(parent=parent)
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
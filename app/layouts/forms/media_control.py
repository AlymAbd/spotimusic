from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QSlider, QSplitter
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from app.core.utils import Icons


class MediaControl(QWidget):
    grandparent: QWidget = None

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)
        self.grandparent = parent.parent()

        self.layout = QVBoxLayout()

        self.track_control = TrackControl(self, self.grandparent)
        self.track_control.setMinimumWidth(600)

        self.audio_control = AudioControl(self, self.grandparent)
        self.audio_control.setMinimumWidth(600)

        self.layout.addWidget(self.track_control,
                              alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.audio_control)

        self.setLayout(self.layout)


class TrackControl(QWidget):
    """
    Buttons next, prev, play, pause, stop, add/remove to favorite
    """

    NEXT_TRACK_STOP = 0
    NEXT_TRACK_PLAY_NEXT = 1
    NEXT_TRACK_REPEAT_CURRENT = 2
    NEXT_TRACK_REPEAT_PLAYLIST = 3

    grandparent: QWidget = None
    current_next_track_behaviour = NEXT_TRACK_PLAY_NEXT

    def __init__(self, parent: QWidget | None, grandparent: QWidget | None) -> None:
        super().__init__(parent=parent)
        self.grandparent = grandparent
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
        self.timer.start(900)

        self.button_add = QPushButton()
        self.button_add.setIcon(QIcon(Icons('interface.heart').str))
        self.button_add.setToolTip('Add to favorite')
        self.button_add.setMaximumSize(30, 30)

        self.button_similar = QPushButton()
        self.button_similar.setIcon(QIcon(Icons('web.star-half').str))
        self.button_similar.setToolTip('Show recomendations')
        self.button_similar.setMaximumSize(30, 30)

        self.button_shuffle = QPushButton()
        self.button_shuffle.setIcon(QIcon(Icons('media.shuffle').str))
        self.button_shuffle.setToolTip('Shuffle playlist')
        self.button_shuffle.setMaximumSize(30, 30)

        self.button_action_next = QPushButton()
        self.button_action_next.setToolTip('Repeat current track')
        self.button_action_next.setIcon(
            QIcon(Icons('direction.angle-double-right').str)
        )
        self.button_action_next.setMaximumSize(30, 30)
        self.button_action_next.clicked.connect(self.next_track_behaviour)

        self.volume_control = VolumeControl(self, self.grandparent)

        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.setMinimumWidth(1)
        splitter.setMaximumWidth(5)

        self.layout.addWidget(self.button_shuffle,
                              alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.button_action_next,
                              alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(splitter)
        self.layout.addWidget(
            self.button_add, alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.button_similar,
                              alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(splitter)

        self.layout.addWidget(
            self.button_prev, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(
            self.button_stop, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.button_play_pause,
                              alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(
            self.button_next, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(splitter)

        self.layout.addWidget(self.volume_control,
                              alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(self.layout)

    def next_track_behaviour(self):
        next_behaviour = self.current_next_track_behaviour
        icon = None
        title = ""

        if self.current_next_track_behaviour == 3:
            next_behaviour = self.NEXT_TRACK_STOP
        else:
            next_behaviour += 1
        self.current_next_track_behaviour = next_behaviour

        match next_behaviour:
            case self.NEXT_TRACK_PLAY_NEXT:
                icon = 'direction.angle-double-right'
                title = 'Continue in playlist'
            case self.NEXT_TRACK_REPEAT_CURRENT:
                icon = 'interface.infinite'
                title = 'Repeat current track'
            case self.NEXT_TRACK_REPEAT_PLAYLIST:
                icon = 'direction.shift-right'
                title = 'Repeat current playlist'
            case self.NEXT_TRACK_STOP:
                icon = 'web.ban'
                title = 'Do not continue'
        self.button_action_next.setToolTip(title)
        self.button_action_next.setIcon(
            QIcon(Icons(icon).str)
        )

    def handle_next_track_behaviour(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            match self.current_next_track_behaviour:
                case self.NEXT_TRACK_PLAY_NEXT:
                    self.media_next()
                case self.NEXT_TRACK_REPEAT_CURRENT:
                    self.parent().audio_control.slider_position_moved(0.1)
                    self.media_playpause(True)
                case self.NEXT_TRACK_REPEAT_PLAYLIST:
                    self.media_next()
                case self.NEXT_TRACK_STOP:
                    self.media_stop()

    def media_stop(self):
        self.grandparent.media_player.stop()
        self.grandparent.track_list.current_track_info.update_info({})

    def media_playpause(self, value=None):
        if not self.grandparent.media_player.isPlaying() or value:
            self.button_play_pause.setIcon(QIcon(Icons('media.pause').str))
            self.grandparent.media_player.play()
            self.button_play_pause.setChecked(True)
            self.update_current_seek_position()
        else:
            self.button_play_pause.setIcon(QIcon(Icons('media.play').str))
            self.grandparent.media_player.pause()
            self.button_play_pause.setChecked(False)

    def media_next(self):
        current_index = self.grandparent.track_list.track_list.indexFromItem(
            self.grandparent.track_list.track_list.currentItem()
        ).row()
        next_index = current_index + 1
        if (next_index + 1) > self.grandparent.track_list.track_list.count():
            next_index = 0
        self._change_track(next_index)

    def media_prev(self):
        current_index = self.grandparent.track_list.track_list.indexFromItem(
            self.grandparent.track_list.track_list.currentItem()).row()
        next_index = current_index - 1
        if (next_index < 0):
            next_index = self.grandparent.track_list.track_list.count() - 1
        self._change_track(next_index)

    def _change_track(self, index):
        self.grandparent.media_player.stop()
        next_item = self.grandparent.track_list.track_list.item(index)
        next_item.setSelected(True)
        self.grandparent.track_list.track_list.setCurrentItem(next_item)
        self.grandparent.track_list.play_selected_music(next_item)

    def update_current_seek_position(self):
        position = self.grandparent.media_player.position() or 0
        duration = self.grandparent.media_player.duration() or 1
        self.parent().audio_control.slider_position.setValue(
            int(position/duration*1000)
        )
        self.parent().audio_control.label.setText(
            f'{self.format_time(position)} / {self.format_time(self.grandparent.media_player.duration())}')

    def format_time(self, milliseconds):
        minutes, seconds = divmod(milliseconds // 1000, 60)
        return f'{minutes:02d}:{seconds:02d}'


class AudioControl(QWidget):
    """
    Track position, track info
    """
    grandparent = None

    def __init__(self, parent: QWidget | None, grandparent: QWidget | None) -> None:
        super().__init__(parent=parent)
        self.grandparent = grandparent

        self.layout = QHBoxLayout()
        self.label = QLabel('00:00 | 00:00')
        self.slider_position = QSlider(Qt.Orientation.Horizontal)
        self.slider_position.setMinimumSize(100, 10)
        self.slider_position.setMaximum(1000)
        self.slider_position.setMinimum(0)
        self.slider_position.sliderReleased.connect(self.slider_position_moved)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.slider_position)
        self.setLayout(self.layout)

    def slider_position_moved(self, value=None):
        value = value or self.slider_position.value()
        duration = self.grandparent.media_player.duration()
        new_position = value * duration / self.slider_position.maximum()
        self.grandparent.media_player.setPosition(int(new_position))


class VolumeControl(QWidget):
    grandparent = None

    def __init__(self, parent: QWidget | None, grandparent: QWidget | None) -> None:
        super().__init__(parent)
        self.grandparent = grandparent

        self.layout = QHBoxLayout()

        self.slider_volume = QSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setMinimumSize(50, 20)
        self.slider_volume.setMaximumSize(150, 20)
        self.slider_volume.valueChanged.connect(self.change_volume)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(self.grandparent.current_volume)

        self.button_mute = QPushButton()
        self.button_mute.setToolTip('Mute')
        self.button_mute.setIcon(QIcon(Icons('media.volume-mute').str))
        self.button_mute.setMaximumSize(30, 30)
        self.button_mute.setCheckable(True)
        self.button_mute.clicked.connect(self.audio_mute)

        self.layout.addWidget(self.button_mute)
        self.layout.addWidget(self.slider_volume)
        self.setLayout(self.layout)

    def change_volume(self, value):
        self.grandparent.audio_output.setVolume(float(value/100))
        self.grandparent.current_volume = value

    def audio_mute(self, value):
        self.grandparent.audio_output.setMuted(value)

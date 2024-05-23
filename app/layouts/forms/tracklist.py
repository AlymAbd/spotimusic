from PyQt6.QtWidgets import QWidget, QListWidget, QHBoxLayout, QListWidgetItem
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon
from spotipy import Spotify
from .current_track import CurrentTrack
from app.layouts.widgets.widgets import MultiLabelWidget
from app.core.utils import AlbumCover
from app import CACHE_MUSIC_PATH
from os import path
from pydub.utils import mediainfo
from app.core.workers import WorkerA, WorkerB, WorkerC


class TrackList(QWidget):
    client: Spotify = None
    media_player = None
    media_list = None
    track_list = None
    current_track = {}
    current_playlist = {}
    layout = None

    download_worker_a = None
    download_worker_b = None
    download_worker_c = None

    _worker_a_busy: bool = False
    _worker_b_busy: bool = False
    _worker_c_busy: bool = False

    offset = 0
    limit = 100
    prev_page_exist: bool = False
    next_page_exist: bool = False
    current_page: int = 0
    total_page: int = 0

    scrollbar = None
    current_track_info = None

    def __init__(self, parent):
        super().__init__()
        self.media_list = parent
        self.client = parent.client
        self.media_player = parent.media_player
        layout = QHBoxLayout()

        self.track_list = QListWidget()
        self.track_list.setMinimumSize(250, 100)
        self.track_list.itemDoubleClicked.connect(self.play_selected_music)

        self.scrollbar = self.track_list.verticalScrollBar()
        self.scrollbar.valueChanged.connect(self.handle_scrollbar)

        self.current_track_info = CurrentTrack(self)

        layout.addWidget(self.track_list)
        layout.addWidget(self.current_track_info)
        self.setLayout(layout)

        self.download_worker_a = WorkerA(self)
        self.download_worker_a.update_signal.connect(
            self.play_selected_music,
        )
        self.download_worker_a.busy_signal.connect(
            self.check_busy_aworker
        )

        self.download_worker_b = WorkerB(self)
        self.download_worker_b.update_signal.connect(
            self.update_album_cover)

        self.download_worker_b.busy_signal.connect(
            self.check_busy_bworker)

        # self.download_worker_c = WorkerC(self)
        # self.download_worker_c.update_signal.connect(
        #     self.media_list.download_all_info
        # )
        # self.download_worker_c.busy_signal.connect(
        #     self.check_busy_cworker
        # )

    def handle_scrollbar(self, value):
        pass

    def load_tracks(self, playlist=None, offset=None, limit=None):
        playlist = playlist if playlist else self.current_playlist
        self.current_playlist = playlist
        offset = offset if offset else self.offset
        limit = limit if limit else self.limit

        if not playlist.get('id') or playlist.get('id') == 0:
            result = self.load_favorite(limit, offset)
        else:
            result = self.client.playlist_tracks(
                playlist['id'],
                limit=limit,
                offset=offset,
            )
            self.prev_page_exist = result['previous']
            self.next_page_exist = result['next']

        self.render_tracks(result)

    def load_favorite(self, limit: int = 50, offset: int = 0):
        result = []

        if limit > 50:
            limit = 50

        for i in range(2):
            response = self.client.current_user_saved_tracks(
                limit=limit,
                offset=offset
            )
            self.prev_page_exist = response['previous']
            self.next_page_exist = response['next']
            result += response['items']
            offset += 50
        result = {
            'items': result
        }
        self.offset = offset
        return result

    def render_tracks(self, result):
        for track in result['items']:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, {
                'id': track['track']['id'],
                'name': track['track']['name'],
                'type': 'track',
                'album_id': track['track']['album']['id'],
                'album_name': track['track']['album']['name'],
                'album_image_url': track['track']['album']['images'][0]['url'],
                'main_artist_name': track['track']['artists'][0]['name'],
                'artists': [x['name'] for x in track['track']['artists']],
            })
            multi_label_widget = MultiLabelWidget(
                [track['track']['name']],
                [track['track']['artists'][0]['name']],
                [],
                track['track']['album']['id']
            )
            item.setSizeHint(multi_label_widget.sizeHint())
            self.track_list.addItem(item)
            self.track_list.setItemWidget(item, multi_label_widget)

    def check_busy_aworker(self, value):
        self.worker_a_busy = value

    def check_busy_bworker(self, value):
        self.worker_b_busy = value

    def check_busy_cworker(self, value):
        self.worker_c_busy = value

    @property
    def worker_a_busy(self):
        return self._worker_a_busy

    @worker_a_busy.setter
    def worker_a_busy(self, value):
        self._worker_a_busy = value

    @property
    def worker_b_busy(self):
        return self._worker_b_busy

    @worker_b_busy.setter
    def worker_b_busy(self, value):
        self._worker_b_busy = value

    @property
    def worker_c_busy(self):
        return self._worker_c_busy

    @worker_c_busy.setter
    def worker_c_busy(self, value):
        self._worker_c_busy = value

    def play_selected_music(self, item):
        track_data = item.data(Qt.ItemDataRole.UserRole) if isinstance(
            item, QListWidgetItem) else item
        self.current_track = track_data
        self.current_track_info.update_info(track_data, True)
        self.media_list.media_control.track_control.media_stop()
        self.update_album_cover(track_data)
        self.setWindowTitle(
            self.current_playlist['name'] + ': ' + self.current_track['name'])
        file_path = path.join(CACHE_MUSIC_PATH, track_data['id'] + '.mp3')

        if not path.isfile(file_path):
            self.media_list.setDisabled(True)
            # self.download_worker_a.set_data(
            #     'play_track', track_data)
            # self.download_worker_a.start()
            # return
            WorkerA().download_track(track_data)

        self.current_track_info.update_info(track_data)
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.media_list.media_control.track_control.media_playpause(True)
        self.media_list.status_bar.showMessage('')
        self.update_meta(file_path)
        self.media_list.setDisabled(False)

    def download_cover(self, track_data: dict):
        self.download_worker_b.set_data('update_cover', track_data)
        self.download_worker_b.start()

    def update_meta(self, track_path: str):
        info = mediainfo(track_path)
        self.media_list.status_bar.showMessage(
            f"Bitrate: {int(info['bit_rate']) / 1000} kbps, "
            f"Sample Rate: {info['sample_rate']} Hz, "
            f"Codec: {info['codec_name']}, "
            f"Channels: {info['channels']}"
        )
        del info

    def update_album_cover(self, track_data):
        """Alias for update_info -> CurrentTrack"""
        self.current_track_info.update_info(track_data)
        current_item = self.track_list.currentItem()
        if current_item:
            multi_label_widget = self.track_list.itemWidget(current_item)
            if isinstance(multi_label_widget, MultiLabelWidget) and not multi_label_widget.album_cover_setted and AlbumCover.cover_exist(track_data['album_id']):
                multi_label_widget.icon_label.setPixmap(
                    QIcon(AlbumCover.get_path(
                        album_id=track_data['album_id'])
                    ).pixmap(40, 40)
                )

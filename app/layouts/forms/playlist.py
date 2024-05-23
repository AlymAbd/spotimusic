import requests
from os import path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from app import CACHE_IMAGE_PATH
from app.layouts.widgets.widgets import MultiLabelWidget
from spotipy import Spotify


class Playlist(QWidget):
    client: Spotify = None
    media_player = None
    current_playlist = {}

    _offset = 0
    limit = 10

    prev_page_exist: bool = False
    next_page_exist: bool = False
    current_page: int = 0
    total_page: int = 0

    scrollbar = None
    layout: QVBoxLayout = None
    playlist: QListWidget = None

    # parent
    media_list = None

    def __init__(self, parent: QWidget = None) -> None:
        """ Playlists, suggestions, albums """
        super().__init__()
        self.media_list = parent
        self.client = parent.client
        self.media_player = parent.media_player

        self.layout = QVBoxLayout()

        self.playlist = QListWidget()
        self.playlist.setMinimumSize(250, 100)
        self.layout.addWidget(self.playlist)

        self.scrollbar = self.playlist.verticalScrollBar()
        self.scrollbar.valueChanged.connect(self.handle_scrollbar)

        self.setLayout(self.layout)
        self.load_paylists(self.limit, self.offset)

    def load_paylists(self, limit, offset):
        self.media_list.setDisabled(True)
        result = self.client.current_user_playlists(
            limit=limit,
            offset=offset
        )

        self.prev_page_exist = result['previous']
        self.next_page_exist = result['next']

        self.render_playlists_list(result['items'])
        self.media_list.setDisabled(False)

    def render_playlists_list(self, playlist_list: list):
        multi_label_widget = MultiLabelWidget(
            big_text=['Favorite'],
            medium_text=[],
            small_text=['Your favorite track'],
            album_id='',
            delimiter=True
        )
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, {
            'id': 0,
            'name': 'Favorite',
            'type': 'favorite'
        })
        item.setSizeHint(multi_label_widget.sizeHint())
        self.playlist.addItem(item)
        self.playlist.setItemWidget(item, multi_label_widget)

        for playlist in playlist_list:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, {
                'id': playlist['id'], 'type': 'playlist'
            })

            item.setData(Qt.ItemDataRole.UserRole, {
                'id': playlist['id'],
                'name': playlist['name'],
                'type': 'playlist',
            })

            playlist_image = path.join(
                CACHE_IMAGE_PATH, playlist['id'] + '.jpg')
            if not path.isfile(playlist_image):
                response = requests.get(playlist['images'][0]['url'])
                if response.status_code == 200:
                    with open(playlist_image, 'wb') as file:
                        file.write(response.content)

            multi_label_widget = MultiLabelWidget(
                big_text=[playlist['name']],
                medium_text=[],
                small_text=[playlist['description']],
                album_id=playlist['id']
            )

            item.setSizeHint(multi_label_widget.sizeHint())
            self.playlist.addItem(item)
            self.playlist.setItemWidget(item, multi_label_widget)

    def play_selected_music(self):
        pass

    def handle_scrollbar(self):
        pass

    def update_album_cover(self):
        pass

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        if value < 0:
            self._offset = 0
        else:
            self._offset = 0

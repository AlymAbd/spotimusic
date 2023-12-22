from PyQt6.QtWidgets import QWidget, QMainWindow
from gui.forms import Auth, Playlist
from gui.config import AuthConfig

class App(QMainWindow):
    auth_config = AuthConfig()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Player')
        if self.auth_config.is_authorized():
            self.setGeometry(500, 500, 500, 500)
            self.show_playlist()
        else:
            self.setGeometry(500, 500, 500, 500)
            self.main_widget = Auth(self)
            self.set_ui(self.main_widget)

        self.setCentralWidget(self.ui)
        self.show()

    def set_ui(self):
        self.setCentralWidget(self.main_widget)
        self.show()

    def show_playlist(self):
        self.main_widget = Playlist(self)
        self.set_ui()

from PyQt6.QtWidgets import QWidget, QMainWindow
from .forms import Auth, Playlist
from app.config import AuthConfig

class App(QMainWindow):
    auth_config = AuthConfig()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Player')
        if self.auth_config.is_authorized():
            self.setGeometry(500, 500, 500, 500)
            self.w = Playlist(self)
            self.hide()
            self.w.show()
        else:
            self.setGeometry(500, 500, 500, 500)
            self.ui = Auth(self)
            self.ui.set_ui()
            self.show()

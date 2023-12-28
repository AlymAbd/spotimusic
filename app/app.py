from PyQt6.QtWidgets import QWidget, QMainWindow, QToolBar, QStatusBar, QWidgetAction, QLabel
from .forms import Auth, Playlist, Settings
from .config import config_exist, secret_exist

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        action_home = QWidgetAction(self)
        action_home.setText("Home page")
        action_home.triggered.connect(self.load_page)

        action_settings = QWidgetAction(self)
        action_settings.setStatusTip("Setup player here")
        action_settings.setText("Settings")
        action_settings.triggered.connect(self.load_settings)

        action_logout = QWidgetAction(self)
        action_logout.setText("Logout")

        action_exit = QWidgetAction(self)
        action_exit.setText("Exit")
        action_exit.triggered.connect(self.close)

        menu = self.menuBar()
        file_menu = menu.addMenu("&Menu")
        file_menu.addAction(action_home)
        file_menu.addAction(action_settings)
        file_menu.addAction(action_logout)
        file_menu.addAction(action_exit)

        self.setWindowTitle('Player')
        self.setGeometry(500, 500, 500, 500)

        self.load_page()

    def load_page(self):
        if not secret_exist():
            self.load_settings()
        elif config_exist():
            self.load_playlist()
        else:
            self.load_authpage()

    def load_settings(self):
        central_widget = Settings(self)
        self.setCentralWidget(central_widget)

    def load_playlist(self):
        central_widget = Playlist(self)
        self.setCentralWidget(central_widget)

    def load_authpage(self):
        central_widget = Auth(self)
        self.setCentralWidget(central_widget)

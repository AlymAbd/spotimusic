from gui.client import spotify_oauth
from gui.forms import BaseLayout
from auth.app import Server

from datetime import datetime, timedelta
from os import path, remove
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLabel
import webbrowser
import uvicorn
import time

# minutes
TIMEOUT = 1

class Auth(BaseLayout):
    def setup_ui(self):
        self.layout = QVBoxLayout(self.parent)

        self.parent.setWindowTitle("Login page")
        self.parent.setGeometry(500, 500, 300, 300)

        self.button_login = QPushButton("Authorize",)
        self.button_login.setMinimumSize(80, 80)
        self.button_login.clicked.connect(self.handle_auth)

        self.label_auth_status = QLabel("")

        self.layout.addWidget(self.button_login)
        self.layout.addWidget(self.label_auth_status)

    def translate(self):
        pass

    def handle_auth(self):
        self.button_login.setDisabled(True)
        # double auth check
        if not self.parent.auth_config.is_authorized():
            # start auth callback web-server

            timeout_time = datetime.now() + timedelta(minutes=TIMEOUT)
            config = uvicorn.Config("auth.app:app", host="0.0.0.0", port=6789, log_level="info")
            server = Server(config=config)

            with server.run_in_thread():

                uri = spotify_oauth.get_authorize_url()
                kill_thread_fpath = path.join(self.parent.auth_config.base_path, 'kill_thread')

                webbrowser.open(uri)

                while not path.exists(kill_thread_fpath):
                    if datetime.now() > timeout_time:
                        self.label_auth_status.setText("Timeout... try again...")
                        print('timeout... shutting down...')
                    time.sleep(5)

                if path.exists(kill_thread_fpath):
                    remove(kill_thread_fpath)
                    self.parent.show_playlist()
                else:
                    self.label_auth_status.setText("Something went wrong, please try again later")
        else:
            self.parent.show_playlist()

        self.button_login.setVisible(False)

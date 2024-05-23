import webbrowser
import uvicorn
import time
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel
)
# minutes
TIMEOUT = 1


class Auth(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.parent = parent
        if callable(parent):
            self.parent = parent()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setWindowTitle("Login page")
        self.setGeometry(500, 500, 300, 300)

        self.button_login = QPushButton("Authorize")
        self.button_login.setMinimumSize(80, 80)
        self.button_login.clicked.connect(self.handle_auth)

        self.label_auth_status = QLabel("")

        self.layout.addWidget(self.button_login)
        self.layout.addWidget(self.label_auth_status)

    def handle_auth(self):
        from app.core.client import Client
        from auth_server.server import Server, ExitEvent

        client = Client()

        self.button_login.setDisabled(True)
        # double auth check
        if client.is_expired():
            # start auth callback web-server

            timeout_time = datetime.now() + timedelta(minutes=TIMEOUT)
            config = uvicorn.Config(
                "auth_server.server:app", host="localhost", port=6789, log_level="info")
            server = Server(config=config)

            with server.run_in_thread():
                ExitEvent.set()
                uri = client.spotify_oauth.get_authorize_url()
                webbrowser.open(uri)
                self.label_auth_status.setText(f"Timeout is :{timeout_time}")

                while ExitEvent.is_set():
                    if datetime.now() > timeout_time:
                        self.label_auth_status.setText(
                            "Timeout... try again...")
                        print('timeout... shutting down...')
                        break
                    time.sleep(5)
                ExitEvent.clear()
                self.parent.load_playlist()
        else:
            self.parent.load_playlist()

        self.button_login.setVisible(False)

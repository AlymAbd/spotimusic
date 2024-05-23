from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel
)


class Debug(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent=parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label_worker_a_status = QLabel("Worker A:")
        self.label_worker_b_status = QLabel("Worker B:")
        self.label_worker_c_status = QLabel("Worker C:")

        self.audio_info = QLabel()

        self.clear_cache_button = QPushButton("Clear cache")

        self.layout.addWiget(self.label_worker_a_status)
        self.layout.addWiget(self.label_worker_b_status)
        self.layout.addWiget(self.label_worker_c_status)
        self.layout.addWiget(self.audio_info)
        self.layout.addWiget(self.clear_cache_button)

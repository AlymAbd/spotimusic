from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget, QMainWindow


class BaseLayout(QWidget):
    parent = None
    def __init__(self, parent) -> None:
        self.parent: QWidget = parent

    @abstractmethod
    def setup_ui(self):
        pass

    @abstractmethod
    def translate(self):
        pass

    def set_ui(self):
        self.setup_ui()
        self.translate()

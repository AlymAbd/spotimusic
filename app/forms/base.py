from PyQt6.QtWidgets import QWidget

class BaseWidget(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent = parent)

    def insert_widget(self, widget):
        self.layout.addWidget(widget)


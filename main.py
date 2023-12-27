import sys
from app.app import App
from app.database import Migration
from PyQt6.QtWidgets import QApplication

migration = Migration()
migration.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())

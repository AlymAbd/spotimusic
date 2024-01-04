from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFormLayout, QLineEdit, QPushButton
from app.util import random_string
from app.models import Secrets
from app.database.entity import Entity


class Settings(QWidget):
    data: dict = {}
    obj: Entity = None

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.obj = Secrets.get_first().load()
        self.data = self.obj.values

        if not self.data.get('state'):
            self.data['state'] = random_string(25)
        if not self.data.get('redirect_uri'):
            self.data['redirect_uri'] = 'http://0.0.0.0:6789/callback'

        self.setWindowTitle('Player settings')
        self.add_inputs()

    def add_inputs(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.form_input = Form(self)

        button_save = QPushButton('Save', self)
        button_save.clicked.connect(self.save_data)
        self.layout.addWidget(button_save)

        button_back = QPushButton('Back', self)
        button_back.clicked.connect(self.click_back)
        self.layout.addWidget(button_back)

    def save_data(self):
        client_id = self.form_input.input_client_id.text()
        redirect_uri = self.form_input.input_redirect_uri.text()
        secret = self.form_input.input_secret.text()
        state = self.form_input.input_state.text()
        self.obj.set_value('client_id', client_id)
        self.obj.set_value('redirect_uri', redirect_uri)
        self.obj.set_value('secret', secret)
        self.obj.set_value('state', state)
        self.obj.save()

    def click_back(self):
        self.parent().load_page()


class Form(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.widget = QWidget(self)
        self.layout = QFormLayout()

        self.input_client_id = QLineEdit(self)
        self.input_client_id.setText(self.parent().data.get('client_id'))
        self.layout.addWidget(self.create_labeled_input(
            'Client ID*', self.input_client_id))

        self.input_secret = QLineEdit(self)
        self.input_secret.setText(self.parent().data.get('secret'))
        self.layout.addWidget(self.create_labeled_input(
            'Secret', self.input_secret))

        self.input_redirect_uri = QLineEdit(self)
        self.input_redirect_uri.setText(self.parent().data.get('redirect_uri'))
        self.layout.addWidget(self.create_labeled_input(
            'Redirect URL', self.input_redirect_uri))

        self.input_state = QLineEdit(self)
        self.input_state.setText(self.parent().data.get('state'))
        self.input_state.setReadOnly(True)
        self.layout.addWidget(
            self.create_labeled_input('State', self.input_state))

        self.setLayout(self.layout)
        parent.layout.addWidget(self)

    def create_labeled_input(self, label_text, input_widget):
        widget = QWidget(self)
        layout = QFormLayout()
        widget.setLayout(layout)
        label = QLabel(label_text, self)
        layout.addWidget(label)
        layout.addWidget(input_widget)
        return widget

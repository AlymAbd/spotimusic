from app.core.base_entity import BaseEntity


class Secrets(BaseEntity):
    fields = {
        'client_id': {},
        'redirect_uri': {'default': 'http://localhost:6789/callback'},
        'secret': {},
        'state': {},
    }

    filename = 'auth'

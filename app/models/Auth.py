from ..database import models

class Secrets(models.OneRecordModel):
    primary_key = 'client_id'

    client_id = models.String()
    redirect_uri = models.String()
    secret = models.String()
    state = models.String()

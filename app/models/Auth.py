from ..database import models

class Secrets(models.OneRecordModel):
    client_id = models.String()
    redirect_uri = models.String()
    secret = models.String()
    state = models.String()

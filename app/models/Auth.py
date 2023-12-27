from ..database import models

class Secrets(models.OneRecordModel):
    client_id = models.String()
    redirect_uri = models.String()
    secret = models.String()
    state = models.String()

class Oauth(models.OneRecordModel):
    access_token = models.String()
    refresh_token = models.String()
    token_type = models.String()
    expires_in = models.Integer()
    expires_at = models.Datetime()
    scope = models.String()

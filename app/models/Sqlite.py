from ..database import models

class SqliteMaster(models.Model):
    _table_name = 'sqlite_master'

    Type = models.String()
    name = models.String()
    tbl_name = models.String()
    rootpage = models.String()


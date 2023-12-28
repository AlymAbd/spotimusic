from ..database import models
from datetime import datetime

class Migration(models.Model):
    date = models.Datetime()
    migration_name = models.String()

    @classmethod
    def create_migration_record(cls, module_name):
        obj = cls.new_object()
        obj.set_value('date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        obj.set_value('migration_name', module_name)
        return obj.save()


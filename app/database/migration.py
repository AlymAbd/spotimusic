from .models import Model
from .database import db_cursor
from app import generate_path
from inspect import isclass
import glob
from os.path import isfile, basename
from importlib import util
from app import models


MIGRATION_PATH = generate_path(pathes=('database', 'migrations'))

class Migration(object):
    model: Model = None

    def __init__(self, model: Model = None) -> None:
        if model or (self.model):
            model = self.model
            self.model = model()

    def start(self):
        exist_migrations = self._get_exist_migrations()
        migration_path = generate_path(pathes=(MIGRATION_PATH, '*.py'))
        migrations = [basename(f)[:-3] for f in glob.glob(migration_path)
                            if isfile(f)
                            and not f.endswith('__init__.py')
                            and basename(f)[:-3] not in exist_migrations
                    ]
        for module_name in migrations[::-1]:
            module = self._load_module(module_name)
            self._handle_module_migrations(module)

    def _get_exist_migrations(self):
        exist = []
        if not self._migration_table_exist():
            init_migration = '000_migrations'
            module = self._load_module(init_migration)
            self._handle_module_migrations(module)

        objs = models.Migration.get_all()
        objs.select('*')
        objs.order('date')
        exist = objs.load(False)
        return [x['migration_name'] for x in exist]

    def _migration_table_exist(self):
        migration_model = models.Migration()
        data = models.SqliteMaster.get_first()
        data.select('COUNT(*) as count')
        data.where("type='table'", f"name='{migration_model.table_name}'")
        data = data.load().count
        return data

    def _load_module(self, module_name):
        spec = util.spec_from_file_location(module_name, generate_path(MIGRATION_PATH, pathes=(module_name+'.py')))
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _handle_module_migrations(self, module):
        items = [x for x in dir(module) if not x.startswith('__') and self._check_item(module, x)]
        for item in items:
            item: Migration = getattr(module, item)()
            item.migrate()
        models.Migration.create_migration_record(module.__name__)

    def _check_item(self, module, item):
        if item == 'Migration':
            return False

        item = getattr(module, item)
        if isclass(item):
            item = item()
            if isinstance(item, Migration):
                return True

    """
    Method for manipulation with table (CREATE, UPDATE, DROP)
    """
    def ddl(self) -> str:
        pass

    """
    Method for manipulation with data (INSERT, DELETE, UPDATE)
    """
    def sql(self) -> str:
        pass

    def migrate(self):
        ddl = self.ddl()
        sql = self.sql()
        if ddl:
            db_cursor.execute(ddl)
        if sql:
            db_cursor.execute(sql)

import sqlite3
from app import TEMP_PATH, generate_path

database = sqlite3.connect(generate_path(
    TEMP_PATH, ('database', 'database.db')))
db_cursor = database.cursor()

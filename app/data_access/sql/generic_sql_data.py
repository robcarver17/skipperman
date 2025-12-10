import sqlite3
from os.path import join, exists
from pathlib import Path

SQL_FILE_NAME = "skipperman.db"


class GenericSqlData(object):
    def __init__(self, master_data_path: str, backup_data_path: str):
        db_file_name = join(master_data_path, SQL_FILE_NAME)
        self._db_file_name = db_file_name
        self._backup_data_path = backup_data_path

        print(self.cursor)

    def table_does_not_exist(self, table_name: str) -> bool:
        listOfTables = self.cursor.execute(
            "SELECT * FROM sqlite_master WHERE type='table' AND name='%s'"% table_name).fetchall()

        no_tables = len(listOfTables)==0

        return no_tables

    @property
    def cursor(self):
        return self.conn.cursor()

    @property
    def conn(self):
        conn = getattr(self, "_conn", None)
        if conn is None:
            conn = sqlite3.connect(self.db_file_name)
            self._conn = conn

        return conn


    @property
    def db_file_name(self):
        return self._db_file_name
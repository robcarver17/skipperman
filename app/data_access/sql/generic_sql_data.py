import sqlite3
from os.path import join

SQL_FILE_NAME = "skipperman.db"


class DBConnection:
    def __init__(self, master_data_path: str):
        db_file_name = join(master_data_path, SQL_FILE_NAME)
        self._db_file_name = db_file_name

    @property
    def db_file_name(self):
        return self._db_file_name

    def close(self):
        self.conn.close()
        delattr(self, "_conn")

    @property
    def conn(self):
        conn = getattr(self, "_conn", None)
        if conn is None:
            conn = sqlite3.connect(self.db_file_name, check_same_thread=False)
            self._conn = conn

        return conn


class GenericSqlData(object):
    def __init__(self, db_connection: DBConnection, object_store: "ObjectStore"):
        self._db_connection = db_connection
        self._object_store = object_store

    @property
    def object_store(self):
        return self._object_store

    def table_does_not_exist(self, table_name: str) -> bool:
        listOfTables = self.cursor.execute(
            "SELECT * FROM sqlite_master WHERE type='table' AND name='%s'" % table_name
        ).fetchall()

        no_tables = len(listOfTables) == 0

        return no_tables

    def close(self):
        self.db_connection.close()

    @property
    def cursor(self):
        return self.conn.cursor()

    @property
    def conn(self):
        return self.db_connection.conn

    @property
    def db_connection(self):
        return self._db_connection



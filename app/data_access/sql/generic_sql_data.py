import datetime
import sqlite3
from os.path import join, exists
from pathlib import Path
from typing import Union

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

    def close(self):
        self.conn.close()
        delattr(self, "_conn")

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

def bool2int(some_bool: bool):
    if some_bool:
        return 1
    else:
        return 0

def int2bool(some_int: int):
    if some_int==1:
        return True
    elif some_int==0:
        return False
    else:
        raise Exception("%s not 0 or 1 and of type %s" % (str(some_int), str(type(some_int))))

def date2int(some_datetime: Union[datetime.date, datetime.datetime]) -> int:
    if type(some_datetime) is datetime.date:
        some_datetime = datetime.datetime(some_datetime.year, some_datetime.month, some_datetime.day, tzinfo=datetime.timezone.utc)
    return int(some_datetime.timestamp())

def int2date(some_int: int) -> Union[datetime.date, datetime.datetime]:
    some_datetime = datetime.datetime.fromtimestamp(float(some_int), datetime.timezone.utc)
    if some_datetime.minute==0:
        if some_datetime.hour==0:
            return datetime.date(some_datetime.year, some_datetime.month, some_datetime.day)

    return some_datetime

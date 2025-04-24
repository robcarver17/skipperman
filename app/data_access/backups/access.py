import datetime
import pathlib

from app.objects.utilities.utils import transform_datetime_into_str, transform_str_into_datetime
import os
from typing import List


NO_BACKUPS_YET = -1


def get_oldest_backup_number(datapath) -> int:
    all_backup_diffs_as_numbers = all_diffs_in_directory(datapath)
    if len(all_backup_diffs_as_numbers) == 0:
        return NO_BACKUPS_YET

    return max(all_backup_diffs_as_numbers)


def datetime_of_backup_number(backup_number: int, datapath: str) -> datetime.datetime:
    backup_directory_for_this_backup = get_backup_directory(
        backup_number=backup_number, datapath=datapath
    )

    return read_timestamp_file(backup_directory_for_this_backup)


def get_backup_directory(backup_number: int, datapath: str) -> str:
    return os.path.join(datapath, "%d" % backup_number)


def all_diffs_in_directory(datapath) -> List[int]:
    try:
        all_backup_difs = os.listdir(datapath)
    except FileNotFoundError:
        return []
    all_backup_diffs_as_numbers = [int(diff) for diff in all_backup_difs]

    return all_backup_diffs_as_numbers


def create_timestamp_file(backup_directory_for_this_backup: str):
    filename = os.path.join(backup_directory_for_this_backup, TIMESTAMP_FILE_NAME)
    with open(filename, "w") as f:
        f.write(transform_datetime_into_str(datetime.datetime.now()))


def read_timestamp_file(backup_directory_for_this_backup: str) -> datetime.datetime:
    filename = os.path.join(backup_directory_for_this_backup, TIMESTAMP_FILE_NAME)
    with open(filename, "r") as f:
        string = f.read()

    return transform_str_into_datetime(string)


def delete_timestamp_file(backup_directory_for_this_backup):
    filename = os.path.join(backup_directory_for_this_backup, TIMESTAMP_FILE_NAME)
    try:
        pathlib.Path.unlink(pathlib.Path(filename))
    except:
        pass


TIMESTAMP_FILE_NAME = "timestamp.txt"

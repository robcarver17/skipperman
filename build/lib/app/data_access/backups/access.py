import datetime
import os
from typing import List


NO_BACKUPS_YET = -1


def get_oldest_backup_number(datapath) -> int:
    all_backup_diffs_as_numbers= all_diffs_in_directory(datapath)
    if len(all_backup_diffs_as_numbers)==0:
        return NO_BACKUPS_YET

    return max(all_backup_diffs_as_numbers)


def datetime_of_backup_number(backup_number: int, datapath: str) -> datetime.datetime:
    backup_dir = os.path.join(datapath, "%d" % backup_number)
    try:
        unixtime = os.path.getmtime(backup_dir)
    except FileNotFoundError:
        raise FileNotFoundError

    return datetime.datetime.fromtimestamp(unixtime)


def get_backup_directory(backup_number: int, datapath: str) -> str:
    return os.path.join(datapath, "%d" % backup_number)


def all_diffs_in_directory(datapath) -> List[int]:
    all_backup_difs = os.listdir(datapath)
    all_backup_diffs_as_numbers = [int(diff) for diff in all_backup_difs]

    return all_backup_diffs_as_numbers

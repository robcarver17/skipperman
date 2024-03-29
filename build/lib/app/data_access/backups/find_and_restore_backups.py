import datetime
import pathlib
import shutil
from typing import Dict
from app.data_access.data import master_data_path
from app.data_access.backups.access import all_diffs_in_directory, datetime_of_backup_number, get_backup_directory,delete_timestamp_file


def dict_of_backups_with_datetimes(datapath) -> Dict[int, datetime.datetime]:
    all_backup_diffs_as_numbers = all_diffs_in_directory(datapath)

    dict_of_backups = dict([
        (diff, datetime_of_backup_number(backup_number=diff, datapath=datapath)) for diff in all_backup_diffs_as_numbers
    ])
    return dict(sorted(dict_of_backups.items(), key=lambda item: item[1], reverse=True))

def restore_backup(backup_diff: int, datapath: str):
    all_backup_diffs_as_numbers = all_diffs_in_directory(datapath)
    try:
        assert backup_diff in all_backup_diffs_as_numbers
    except:
        raise Exception("Can't restore non existent backup %d" % backup_diff)

    backup_dir = get_backup_directory(backup_number=backup_diff, datapath=datapath)
    delete_all_master_data()
    shutil.copytree(backup_dir, master_data_path, dirs_exist_ok=True)
    delete_timestamp_file(master_data_path)

def delete_all_master_data():
    shutil.rmtree(master_data_path)
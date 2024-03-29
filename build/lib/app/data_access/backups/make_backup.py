
import os.path
import shutil
import subprocess

from app.data_access.backups.access import get_oldest_backup_number, get_backup_directory, due_for_another_backup, \
    create_timestamp_file
from app.data_access.configuration.configuration import NUMBER_OF_BACKUPS

def make_backup_if_due(backup_data_path:str, master_data_path: str):
    due = due_for_another_backup(backup_data_path)
    if due:
        make_backup(backup_data_path=backup_data_path, master_data_path=master_data_path)

def make_backup(backup_data_path:str, master_data_path: str):
    remove_oldest_backup_if_too_old(backup_data_path)
    backup_number = get_oldest_backup_number(backup_data_path)
    while backup_number>0:
        move_backup_to_previous_backup(backup_number=backup_number, datapath=backup_data_path)
        backup_number-=1
    if backup_number==0:
        simlink_copy_first_backup(backup_data_path)
    make_first_backup(backup_data_path=backup_data_path, master_data_path=master_data_path)


def remove_oldest_backup_if_too_old(backup_data_path):
    oldest = get_oldest_backup_number(backup_data_path)
    if (oldest+2)>NUMBER_OF_BACKUPS: ## plus 1 because zero indexing, plus another so we end with the right number
        delete_backup_number(backup_number=oldest, backup_data_path=backup_data_path)


def delete_backup_number(backup_number: int, backup_data_path: str):
    backup_dir = get_backup_directory(datapath=backup_data_path, backup_number=backup_number)
    shutil.rmtree(backup_dir)


def move_backup_to_previous_backup(backup_number: int, datapath:str):
    backup_dir = get_backup_directory(backup_number=backup_number, datapath=datapath)
    next_backup_dir = get_backup_directory(backup_number=backup_number + 1, datapath=datapath)
    shutil.copytree(backup_dir, next_backup_dir, dirs_exist_ok=True)


def simlink_copy_first_backup(datapath):

    backup_from = get_backup_directory(backup_number=0, datapath=datapath)
    backup_to = get_backup_directory(backup_number=1, datapath=datapath)
    try:
        shutil.rmtree(backup_to)
    except:
        ## will fail if really first time
        passf
    os.system('cp -al %s %s' % (backup_from, backup_to))
    #subprocess.run(["cp","-al",backup_from, backup_to], cwd=datapath)


def make_first_backup(backup_data_path: str, master_data_path: str):
    backup_directory_for_this_backup = get_backup_directory(backup_number=0, datapath=backup_data_path)
    try:
        os.mkdir(backup_directory_for_this_backup)
    except:
        pass
    subprocess.run(["rsync","-a","--delete", "%s/"% master_data_path,   "%s/" % backup_directory_for_this_backup])
    create_timestamp_file(backup_directory_for_this_backup)

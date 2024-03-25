import os.path
import shutil
import subprocess

from app.data_access.backups.access import get_oldest_backup_number, get_backup_directory
from app.data_access.configuration.configuration import NUMBER_OF_BACKUPS

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
        delete_backup_number(backup_number=oldest, datapath=backup_data_path)


def delete_backup_number(backup_number: int, backup_data_path: str):
    backup_dir = get_backup_directory(datapath=backup_data_path, backup_number=backup_number)
    shutil.rmtree(backup_dir)


def move_backup_to_previous_backup(backup_number: int, datapath:str):
    backup_dir = get_backup_directory(backup_number=backup_number, datapath=datapath)
    next_backup_dir = get_backup_directory(backup_number=backup_number + 1, datapath=datapath)
    shutil.copytree(backup_dir, next_backup_dir, dirs_exist_ok=True)


def simlink_copy_first_backup(datapath):
    backup_dir = get_backup_directory(backup_number=0, datapath=datapath)
    backup_to = get_backup_directory(backup_number=1, datapath=datapath)
    subprocess.run(["cp","-al",backup_dir, backup_to])

def make_first_backup(backup_data_path: str, master_data_path: str):
    backup_dir = get_backup_directory(backup_number=0, datapath=backup_data_path)
    try:
        os.mkdir(backup_dir)
    except:
        pass
    subprocess.run(["rsync","-a","--delete", "%s/"% master_data_path,   "%s/" % backup_dir])

    """
    "rm -rf backup.3"
    mv backup.2 backup.3
    mv backup.1 backup.2
    cp -al backup.0 backup.1
    rsync -a --delete source_directory/  backup.0/
    
        shutil.copytree(temp_dir, master_data_path, dirs_exist_ok=True)
    interface.log_message("Deleting temporary directory")
    shutil.rmtree(temp_dir)

    
    """
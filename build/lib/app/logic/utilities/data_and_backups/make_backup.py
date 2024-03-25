import shutil
import os

from app.data_access.data import master_data_path
from app.data_access.uploads_and_downloads import download_directory
from app.objects.abstract_objects.abstract_form import File



def make_backup_and_return_file() -> File:
    output_filename = backup_file_name_and_path()
    shutil.make_archive(output_filename, 'zip', master_data_path)

    return File(output_filename+".zip")

def backup_file_name_and_path():
    return os.path.join(download_directory, "backup_data")

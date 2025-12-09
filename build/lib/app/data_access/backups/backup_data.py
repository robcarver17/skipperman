from app.data_access.configuration.configuration import BACKUP_DATA
import os

home_directory = os.path.expanduser("~")
import os

backup_data_path = os.path.join(home_directory, BACKUP_DATA)
try:
    os.mkdir(backup_data_path)
except:
    pass

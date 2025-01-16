## In the unlikely event of switching to eg a database change here
from app.data_access.configuration.configuration import DATAPATH
from app.data_access.api.csv_api import CsvDataApi
from app.data_access.store.object_store import ObjectStore
from app.data_access.user_data import user_data_path
from app.data_access.backups.backup_data import backup_data_path
from app.data_access.store.store import Store
import os

home_directory = os.path.expanduser("~")

master_data_path = os.path.join(home_directory, DATAPATH)

try:
    os.mkdir(master_data_path)
except:
    pass


## IF YOU WANT TO USE A DIFFERENT KIND OF DATA, EG DATABASE, CREATE AN API AND MODIFY THIS
def make_data():
    return CsvDataApi(
        master_data_path=master_data_path,
        user_data_path=user_data_path,
        backup_data_path=backup_data_path,
    )


underling_data_api = make_data()
store = Store()

object_store = ObjectStore(data_store=store, data_api=underling_data_api)

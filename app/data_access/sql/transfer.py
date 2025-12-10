
## In the unlikely event of switching to eg a database change here
from app.data_access.csv.csv_api import CsvDataApi
from app.data_access.configuration.configuration import DATAPATH, PICKLE_STORE
from app.data_access.sql.groups import SqlDataListOfCadetsWithGroups
from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_cache import  SimpleObjectCache
from app.data_access.user_data import user_data_path
from app.data_access.backups.backup_data import backup_data_path
import os

home_directory = os.path.expanduser("~")

master_data_path = os.path.join(home_directory, DATAPATH)


def do_transfer():
    csv_api = CsvDataApi(
        master_data_path=master_data_path,
        user_data_path=user_data_path,
        backup_data_path=backup_data_path,
    )

    events = csv_api.data_list_of_events.read()

    sql_groups = SqlDataListOfCadetsWithGroups(master_data_path=master_data_path, backup_data_path=backup_data_path)

    for event in events:
        event_id = event.id
        list_of_cadets_with_groups = csv_api.data_list_of_cadets_with_groups.read(event_id)
        if len(list_of_cadets_with_groups)>0:
            sql_groups.write(list_of_cadets_with_groups, event_id)


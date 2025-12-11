
## In the unlikely event of switching to eg a database change here
from app.data_access.csv.csv_api import CsvDataApi
from app.data_access.configuration.configuration import DATAPATH, PICKLE_STORE
from app.data_access.sql.dinghies_at_event import SqlDataListOfDinghies, SqlDataListOfCadetAtEventWithDinghies
from app.data_access.sql.groups import SqlDataListOfCadetsWithGroups, SqlDataListOfGroups, SqlDataListOfGroupNamesForEventsAndCadetPersistentVersion
from app.data_access.sql.cadets import SqlDataListOfCadets
from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_cache import  SimpleObjectCache
from app.data_access.user_data import user_data_path
from app.data_access.backups.backup_data import backup_data_path
import os

home_directory = os.path.expanduser("~")


master_data_path = os.path.join(home_directory, DATAPATH)
csv_api = CsvDataApi(
    master_data_path=master_data_path,
    user_data_path=user_data_path,
    backup_data_path=backup_data_path,
)

sql_persistent_groups = SqlDataListOfGroupNamesForEventsAndCadetPersistentVersion(master_data_path, backup_data_path)
sql_cadets = SqlDataListOfCadets(master_data_path, backup_data_path)
sql_groups = SqlDataListOfGroups(master_data_path=master_data_path, backup_data_path=backup_data_path)
sql_groups_at_events = SqlDataListOfCadetsWithGroups(master_data_path=master_data_path, backup_data_path=backup_data_path)
sql_list_of_dinghies = SqlDataListOfDinghies(master_data_path=master_data_path, backup_data_path=backup_data_path)
sql_cadets_and_dinghies_at_event = SqlDataListOfCadetAtEventWithDinghies(master_data_path=master_data_path, backup_data_path=backup_data_path)

def transfer_from_csv_to_sql():
    csv_api = CsvDataApi(
        master_data_path=master_data_path,
        user_data_path=user_data_path,
        backup_data_path=backup_data_path,
    )

    events = csv_api.data_list_of_events.read()


    """

    for event in events:
        event_id = event.id
        list_of_cadets_with_groups = csv_api.data_list_of_cadets_with_groups.read(event_id)
        if len(list_of_cadets_with_groups)>0:
            sql_groups_at_events.write(list_of_cadets_with_groups, event_id)

    

    
    list_of_cadets =csv_api.data_list_of_cadets.read()
    sql_cadets.write(list_of_cadets)

    list_of_persistent_groups = csv_api.data_list_of_group_names_for_events_and_cadets_persistent_version.read()
    sql_persistent_groups.write(list_of_persistent_groups)


    sql_groups.delete_table()
    csv_groups = csv_api.data_list_of_groups.read()
    sql_groups.write(csv_groups)
    
    list_of_dinghies=csv_api.data_list_of_dinghies.read()
    sql_list_of_dinghies.write(list_of_dinghies)
    """
    for event in events:
        event_id = event.id
        """
        list_of_cadets_with_groups = csv_api.data_list_of_cadets_with_groups.read(event_id)
        if len(list_of_cadets_with_groups)>0:
            sql_groups_at_events.write(list_of_cadets_with_groups, event_id)
        """
        list_of_cadets_with_dinghies = csv_api.data_list_of_cadets_with_dinghies_at_event.read(event_id)
        sql_cadets_and_dinghies_at_event.write(list_of_cadets_with_dinghies, event_id=event_id)

def transfer_from_sql_to_csv():
    csv_api = CsvDataApi(
        master_data_path=master_data_path,
        user_data_path=user_data_path,
        backup_data_path=backup_data_path,
    )

    events = csv_api.data_list_of_events.read()


    for event in events:
        event_id = event.id
        list_of_cadets_with_groups = sql_groups_at_events.read(event_id)
        if len(list_of_cadets_with_groups)>0:
            csv_api.data_list_of_cadets_with_groups.write(list_of_cadets_with_groups, event_id)

        csv_api.data_list_of_cadets_with_dinghies_at_event.write(sql_cadets_and_dinghies_at_event.read(event_id), event_id=event_id)

    csv_api.data_list_of_groups.write(sql_groups.read())
    csv_api.data_list_of_cadets.write(sql_cadets.read())
    csv_api.data_list_of_group_names_for_events_and_cadets_persistent_version.write(sql_persistent_groups.read())
    csv_api.data_list_of_dinghies.write(sql_list_of_dinghies.read())

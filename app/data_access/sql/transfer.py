
## In the unlikely event of switching to eg a database change here
from app.data_access.csv.csv_api import CsvDataApi
from app.data_access.configuration.configuration import DATAPATH, PICKLE_STORE
from app.data_access.sql.dinghies_at_event import SqlDataListOfDinghies, SqlDataListOfCadetAtEventWithDinghies
from app.data_access.sql.events import SqlDataListOfEvents
from app.data_access.sql.groups import SqlDataListOfCadetsWithGroups, SqlDataListOfGroups, SqlDataListOfGroupNamesForEventsAndCadetPersistentVersion
from app.data_access.sql.cadets import SqlDataListOfCadets
from app.data_access.sql.cadet_committee import SqlDataListOfCadetsOnCommitte
from app.data_access.sql.cadets_at_event import SqlDataListOfCadetsAtEvent
from app.data_access.sql.qualifications import *
from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_cache import  SimpleObjectCache
from app.data_access.sql.sql_and_csv_api import MixedSqlAndCsvDataApi
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

mixed_api = MixedSqlAndCsvDataApi(master_data_path=master_data_path, backup_data_path=backup_data_path, user_data_path=user_data_path)
db_connection = mixed_api.db_connection

sql_persistent_groups = SqlDataListOfGroupNamesForEventsAndCadetPersistentVersion(db_connection)
sql_cadets = SqlDataListOfCadets(db_connection)
sql_groups = SqlDataListOfGroups(db_connection)
sql_groups_at_events = SqlDataListOfCadetsWithGroups(db_connection)
sql_list_of_dinghies = SqlDataListOfDinghies(db_connection)
sql_cadets_and_dinghies_at_event = SqlDataListOfCadetAtEventWithDinghies(db_connection)
sql_qualifications = SqlDataListOfQualifications(db_connection)
sql_cadets_with_qualifications = SqlListOfCadetsWithQualifications(db_connection)
sql_cadets_at_event = SqlDataListOfCadetsAtEvent(db_connection)
sql_cadets_on_committee = SqlDataListOfCadetsOnCommitte(db_connection)
sql_events = SqlDataListOfEvents(db_connection)

def transfer_from_csv_to_sql():
    csv_api = CsvDataApi(
        master_data_path=master_data_path,
        user_data_path=user_data_path,
        backup_data_path=backup_data_path,
    )

    events = csv_api.data_list_of_events.read()
    sql_events.write(events)

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
    sql_cadets_and_dinghies_at_event.delete_table()
    for event in events:
        event_id = str(event.id)
        """
        list_of_cadets_with_groups = csv_api.data_list_of_cadets_with_groups.read(event_id)
        if len(list_of_cadets_with_groups)>0:
            sql_groups_at_events.write(list_of_cadets_with_groups, event_id)
        """

        list_of_cadets_with_dinghies = csv_api.data_list_of_cadets_with_dinghies_at_event.read(event_id)
        sql_cadets_and_dinghies_at_event.write(list_of_cadets_with_dinghies, event_id=event_id)

        list_of_cadets_at_event = csv_api.data_cadets_at_event.read(event_id)
        sql_cadets_at_event.write(list_of_cadets_at_event, event_id=event_id)

    #list_of_qualifications = csv_api.data_list_of_qualifications.read()
    #sql_qualifications.delete_table()
    #sql_qualifications.write(list_of_qualifications)

    #sql_cadets_with_qualifications.delete_table()
    #list_of_cadets_with_qualifications = csv_api.data_list_of_cadets_with_qualifications.read()
    #sql_cadets_with_qualifications.write(list_of_cadets_with_qualifications)

    sql_cadets_on_committee.write(csv_api.data_list_of_cadets_on_committee.read())

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
    csv_api.data_list_of_qualifications.write(sql_qualifications.read())
    csv_api.data_list_of_cadets_with_qualifications.write(sql_cadets_with_qualifications.read())
    csv_api.data_list_of_cadets_on_committee.write(sql_cadets_on_committee.read())
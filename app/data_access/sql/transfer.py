
## In the unlikely event of switching to eg a database change here
from app.data_access.csv.csv_api import CsvDataApi
from app.data_access.configuration.configuration import DATAPATH
from app.data_access.sql.cadets_with_qualifications import SqlListOfCadetsWithQualifications
from app.data_access.sql.connections import SqlDataListOfCadetVolunteerAssociations
from app.data_access.sql.dinghies_at_event import SqlDataListOfCadetAtEventWithDinghies
from app.data_access.sql.boat_classes import SqlDataListOfDinghies
from app.data_access.sql.events import SqlDataListOfEvents
from app.data_access.sql.groups import SqlDataListOfGroups
from app.data_access.sql.list_of_roles_and_teams import SqlDataListOfTeamsAndRolesWithIds
from app.data_access.sql.persistent_groups_at_events import SqlDataListOfGroupNamesForEventsAndCadetPersistentVersion
from app.data_access.sql.groups_at_event import SqlDataListOfCadetsWithGroups
from app.data_access.sql.cadets import SqlDataListOfCadets
from app.data_access.sql.cadet_committee import SqlDataListOfCadetsOnCommitte
from app.data_access.sql.cadets_at_event import SqlDataListOfCadetsAtEvent
from app.data_access.sql.qualifications import *
from app.data_access.sql.skills import SqlDataListOfSkills
from app.data_access.sql.sql_and_csv_api import MixedSqlAndCsvDataApi
from app.data_access.sql.teams import SqlDataListOfTeams
from app.data_access.sql.volunteers import SqlDataListOfVolunteers
from app.data_access.sql.volunteers_with_skills import SqlDataListOfVolunteerSkills
from app.data_access.sql.patrol_boats import SqlDataListOfPatrolBoats
from app.data_access.sql.club_dinghies import SqlDataListOfClubDinghies
from app.data_access.sql.roles import SqlDataListOfRoles
from app.data_access.sql.volunteers_in_roles_at_event import SqlDataListOfVolunteersInRolesAtEvent

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
sql_list_of_volunteers = SqlDataListOfVolunteers(db_connection)
sql_associations = SqlDataListOfCadetVolunteerAssociations(db_connection)
sql_skills = SqlDataListOfSkills(db_connection)
sql_volunteers_with_skills =SqlDataListOfVolunteerSkills(db_connection)
sql_patrol_boats =SqlDataListOfPatrolBoats(db_connection)
sql_club_dinghies = SqlDataListOfClubDinghies(db_connection)
sql_roles = SqlDataListOfRoles(db_connection)
sql_teams = SqlDataListOfTeams(db_connection)
sql_volunteers_with_roles = SqlDataListOfVolunteersInRolesAtEvent(db_connection)
sql_teams_and_roles = SqlDataListOfTeamsAndRolesWithIds(db_connection)

def transfer_from_csv_to_sql():
    csv_api = CsvDataApi(
        master_data_path=master_data_path,
        user_data_path=user_data_path,
        backup_data_path=backup_data_path,
    )
    events = csv_api.data_list_of_events.read()

    """
    sql_events.write(events)

    list_of_cadets =csv_api.data_list_of_cadets.read()
    sql_cadets.write(list_of_cadets)

    list_of_persistent_groups = csv_api.data_list_of_group_names_for_events_and_cadets_persistent_version.read().unique_list()

    sql_persistent_groups.write(list_of_persistent_groups)


    csv_groups = csv_api.data_list_of_groups.read()
    sql_groups.write(csv_groups)
    
    list_of_dinghies=csv_api.data_list_of_dinghies.read()
    sql_list_of_dinghies.write(list_of_dinghies)

    for event in events:
        event_id = str(event.id)
        sql_volunteers_with_roles.write(csv_api.data_list_of_volunteers_in_roles_at_event.read(event_id), event_id=event_id)

        list_of_cadets_with_groups = csv_api.data_list_of_cadets_with_groups.read(event_id)
        if len(list_of_cadets_with_groups)>0:
            sql_groups_at_events.write(list_of_cadets_with_groups, event_id)

        list_of_cadets_with_dinghies = csv_api.data_list_of_cadets_with_dinghies_at_event.read(event_id)
        sql_cadets_and_dinghies_at_event.write(list_of_cadets_with_dinghies, event_id=event_id)

        list_of_cadets_at_event = csv_api.data_cadets_at_event.read(event_id)
        sql_cadets_at_event.write(list_of_cadets_at_event, event_id=event_id)
        

    list_of_qualifications = csv_api.data_list_of_qualifications.read()
    sql_qualifications.write(list_of_qualifications)

    list_of_cadets_with_qualifications = csv_api.data_list_of_cadets_with_qualifications.read()
    sql_cadets_with_qualifications.write(list_of_cadets_with_qualifications)

    sql_cadets_on_committee.write(csv_api.data_list_of_cadets_on_committee.read())
    sql_list_of_volunteers.write(csv_api.data_list_of_volunteers.read())
    """
    #sql_associations.write(csv_api.data_list_of_cadet_volunteer_associations.read())
    #sql_skills.write(csv_api.data_list_of_skills.read())
    #sql_volunteers_with_skills.write(csv_api.data_list_of_volunteer_skills.read())
    #sql_patrol_boats.write(csv_api.data_list_of_patrol_boats.read())
    #sql_club_dinghies.write(csv_api.data_List_of_club_dinghies.read())
    #sql_roles.write(csv_api.data_list_of_roles.read())
    #sql_teams.write(csv_api.data_list_of_teams.read())
    sql_teams_and_roles.write(csv_api.data_list_of_teams_and_roles_with_ids.read())

def transfer_from_sql_to_csv():
    csv_api = CsvDataApi(
        master_data_path=master_data_path,
        user_data_path=user_data_path,
        backup_data_path=backup_data_path,
    )

    events = sql_events.read()
    csv_api.data_list_of_events.write(events)

    for event in events:
        event_id = event.id
        list_of_cadets_with_groups = sql_groups_at_events.read(event_id)
        csv_api.data_list_of_cadets_with_groups.write(list_of_cadets_with_groups, event_id)
        csv_api.data_list_of_cadets_with_dinghies_at_event.write(sql_cadets_and_dinghies_at_event.read(event_id), event_id=event_id)
        csv_api.data_list_of_volunteers_in_roles_at_event.write(sql_volunteers_with_roles.read(event_id),event_id=event_id)

    csv_api.data_list_of_groups.write(sql_groups.read())
    csv_api.data_list_of_cadets.write(sql_cadets.read())
    csv_api.data_list_of_group_names_for_events_and_cadets_persistent_version.write(sql_persistent_groups.read())
    csv_api.data_list_of_dinghies.write(sql_list_of_dinghies.read())
    csv_api.data_list_of_qualifications.write(sql_qualifications.read())
    csv_api.data_list_of_cadets_with_qualifications.write(sql_cadets_with_qualifications.read())
    csv_api.data_list_of_cadets_on_committee.write(sql_cadets_on_committee.read())
    csv_api.data_list_of_volunteers.write(sql_list_of_volunteers.read())
    csv_api.data_list_of_cadet_volunteer_associations.write(sql_associations.read())
    csv_api.data_list_of_skills.write(sql_skills.read())
    csv_api.data_list_of_volunteer_skills.write(sql_volunteers_with_skills.read())
    csv_api.data_List_of_club_dinghies.write(sql_club_dinghies.read())
    csv_api.data_list_of_patrol_boats.write(sql_patrol_boats.read())
    csv_api.data_list_of_roles.write(sql_roles.read())
    csv_api.data_list_of_teams.write(sql_teams.read())
    csv_api.data_list_of_teams_and_roles_with_ids.write(sql_teams_and_roles.read())
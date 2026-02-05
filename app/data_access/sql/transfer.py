
## In the unlikely event of switching to eg a database change here
from app.data_access.csv.csv_api import CsvDataApi
from app.data_access.configuration.configuration import DATAPATH
from app.data_access.sql.cadet_attendance import SqlDataAttendanceAtEventsForSpecificCadet
from app.data_access.sql.cadet_clothing import SqlDataListOfCadetsWithClothingAtEvent
from app.data_access.sql.cadet_food import SqlDataListOfCadetsWithFoodRequirementsAtEvent
from app.data_access.sql.cadets_with_qualifications import SqlListOfCadetsWithQualifications
from app.data_access.sql.cadets_with_ticks import SqlDataListOfCadetsWithTickListItems
from app.data_access.sql.club_dinghy_limits import SqlDataListOfClubDinghyLimits
from app.data_access.sql.connections import SqlDataListOfCadetVolunteerAssociations
from app.data_access.sql.dinghies_at_event import SqlDataListOfCadetAtEventWithDinghies
from app.data_access.sql.boat_classes import SqlDataListOfDinghies
from app.data_access.sql.event_warnings import SqlDataListOfEventWarnings
from app.data_access.sql.events import SqlDataListOfEvents
from app.data_access.sql.field_mapping import SqlDataWAFieldMapping, SqlDataWAFieldMappingTemplates
from app.data_access.sql.group_notes import SqlDataListOfGroupNotesAtEvent
from app.data_access.sql.groups import SqlDataListOfGroups
from app.data_access.sql.identified_cadets_at_event import SqlDataListOfIdentifiedCadetsAtEvent
from app.data_access.sql.identified_volunteers_at_event import SqlDataListOfIdentifiedVolunteersAtEvent
from app.data_access.sql.last_roles_across_events_for_volunteers import SqlDataListOfLastRolesAcrossEventsForVolunteers
from app.data_access.sql.list_of_roles_and_teams import SqlDataListOfTeamsAndRolesWithIds
from app.data_access.sql.mapped_registration_data import SqlDataMappedRegistrationData
from app.data_access.sql.notes import SqlDataListOfNotes
from app.data_access.sql.patrol_boat_labels import SqlDataListOfPatrolBoatLabelsAtEvent
from app.data_access.sql.patrol_boats_with_volunteers_at_event import SqlDataListOfVolunteersAtEventWithPatrolBoats
from app.data_access.sql.persistent_groups_at_events import SqlDataListOfGroupNamesForEventsAndCadetPersistentVersion
from app.data_access.sql.groups_at_event import SqlDataListOfCadetsWithGroups
from app.data_access.sql.cadets import SqlDataListOfCadets
from app.data_access.sql.cadet_committee import SqlDataListOfCadetsOnCommitte
from app.data_access.sql.cadets_at_event import SqlDataListOfCadetsAtEvent
from app.data_access.sql.print_options import sqlDataListOfPrintOptions, SqlDataListOfArrangementOptions
from app.data_access.sql.qualifications import *
from app.data_access.sql.skills import SqlDataListOfSkills
from app.data_access.sql.sql_and_csv_api import MixedSqlAndCsvDataApi
from app.data_access.sql.target_roles_at_event import SqlDataListOfTargetForRoleAtEvent
from app.data_access.sql.teams import SqlDataListOfTeams
from app.data_access.sql.tick_sheet_items import SqlDataListOfTickSheetItems
from app.data_access.sql.tick_sheet_sub_stages import SqlDataListOfTickSubStages
from app.data_access.sql.volunteer_food import SqlDataListOfVolunteersWithFoodRequirementsAtEvent
from app.data_access.sql.volunteers import SqlDataListOfVolunteers
from app.data_access.sql.volunteers_at_event import SqlDataListOfVolunteersAtEvent
from app.data_access.sql.volunteers_with_skills import SqlDataListOfVolunteerSkills
from app.data_access.sql.patrol_boats import SqlDataListOfPatrolBoats
from app.data_access.sql.club_dinghies import SqlDataListOfClubDinghies
from app.data_access.sql.roles import SqlDataListOfRoles
from app.data_access.sql.volunteers_in_roles_at_event import SqlDataListOfVolunteersInRolesAtEvent
from app.data_access.sql.club_dinghies_with_people_at_event import SqlDataListOfVolunteersAtEventWithClubDinghies, SqlDataListOfCadetAtEventWithClubDinghies
from app.data_access.sql.wa_event_mapping import SqlDataWAEventMapping


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
sql_club_dinghies_with_cadets = SqlDataListOfCadetAtEventWithClubDinghies(db_connection)
sql_club_dinghies_with_volunteers = SqlDataListOfVolunteersAtEventWithClubDinghies(db_connection)
sql_event_mappings = SqlDataWAEventMapping(db_connection)
sql_field_mappings = SqlDataWAFieldMapping(db_connection)
sql_template_field_mappings = SqlDataWAFieldMappingTemplates(db_connection)
sql_mapped_registration_data = SqlDataMappedRegistrationData(db_connection)
sql_event_warnings = SqlDataListOfEventWarnings(db_connection)
sql_identified_cadets_at_event = SqlDataListOfIdentifiedCadetsAtEvent(db_connection)
sql_print_options = sqlDataListOfPrintOptions(db_connection)
sql_arrangement_options = SqlDataListOfArrangementOptions(db_connection)
sql_list_of_volunteers_at_event = SqlDataListOfVolunteersAtEvent(db_connection)
sql_identified_volunteers_at_event =SqlDataListOfIdentifiedVolunteersAtEvent(db_connection)
sql_club_boat_limits = SqlDataListOfClubDinghyLimits(db_connection)
sql_volunteers_with_patrol_boats = SqlDataListOfVolunteersAtEventWithPatrolBoats(db_connection)
sql_substages = SqlDataListOfTickSubStages(db_connection)
sql_tick_sheet_items = SqlDataListOfTickSheetItems(db_connection)
sql_targets_at_event  = SqlDataListOfTargetForRoleAtEvent(db_connection)
sql_list_of_cadets_with_food_requirements = SqlDataListOfCadetsWithFoodRequirementsAtEvent(db_connection)
sql_list_of_volunteers_with_food_requirements = SqlDataListOfVolunteersWithFoodRequirementsAtEvent(db_connection)
sql_clothing = SqlDataListOfCadetsWithClothingAtEvent(db_connection)
sql_group_notes = SqlDataListOfGroupNotesAtEvent(db_connection)
sql_notes = SqlDataListOfNotes(db_connection)
sql_patrol_boat_labels = SqlDataListOfPatrolBoatLabelsAtEvent(db_connection)
sql_last_volunteer_roles = SqlDataListOfLastRolesAcrossEventsForVolunteers(db_connection)
sql_attendance=SqlDataAttendanceAtEventsForSpecificCadet(db_connection)
sql_ticks = SqlDataListOfCadetsWithTickListItems(db_connection)

def transfer_from_csv_to_sql():
    csv_api = CsvDataApi(
        master_data_path=master_data_path,
        user_data_path=user_data_path,
        backup_data_path=backup_data_path,
    )
    events = csv_api.data_list_of_events.read()

    list_of_cadets =csv_api.data_list_of_cadets.read()
    for cadet in list_of_cadets:
        sql_attendance.write(
            csv_api.data_attendance_at_events_for_specific_cadet.read(cadet.id),
            cadet_id=cadet.id
        )
        sql_ticks.write(
            csv_api.data_list_of_cadets_with_tick_list_items.read(cadet.id),
            cadet_id=cadet.id
        )

    sql_events.write(events)

    for report_name in ["Allocation report", "Patrol boat report", "Rollcall report", "Sailors with boats report", "Volunteer rota report"]:
        sql_arrangement_options.write(csv_api.data_arrangement_and_group_order_options.read(report_name), report_name=report_name)
        for default in ['', '_default']:
            full_name = "%s%s" % (report_name, default)
            sql_print_options.write(csv_api.data_print_options.read(full_name), report_name=full_name)


    sql_cadets.write(list_of_cadets)

    list_of_persistent_groups = csv_api.data_list_of_group_names_for_events_and_cadets_persistent_version.read().unique_list()

    sql_persistent_groups.write(list_of_persistent_groups)


    csv_groups = csv_api.data_list_of_groups.read()
    sql_groups.write(csv_groups)
    
    sql_list_of_dinghies.write(csv_api.data_list_of_dinghies.read())
    

    sql_substages.write(csv_api.data_list_of_tick_sub_stages.read())

    list_of_templates = csv_api.data_wa_field_mapping_list_of_templates.read()
    for template_name in list_of_templates:
        sql_template_field_mappings.write(csv_api.data_wa_field_mapping_templates.read(template_name), template_name=template_name)
    
    sql_tick_sheet_items.write(csv_api.data_list_of_tick_sheet_items.read())

    sql_club_boat_limits._transfer(csv_api.data_List_of_club_dinghy_limits.read())
    sql_club_dinghies.write(csv_api.data_List_of_club_dinghies.read())

    for event in events:
        event_id = str(event.id)
        sql_clothing.write(csv_api.data_list_of_cadets_with_clothing_at_event.read(event_id), event_id=event_id)
        sql_list_of_volunteers_with_food_requirements.write(csv_api.data_list_of_volunteers_with_food_requirement_at_event.read(event_id), event_id=event_id)
        sql_list_of_cadets_with_food_requirements.write(csv_api.data_list_of_cadets_with_food_requirement_at_event.read(event_id), event_id=event_id)
        sql_targets_at_event.write(csv_api.data_list_of_targets_for_role_at_event.read(event_id), event_id=event_id)
        sql_volunteers_with_patrol_boats.write(csv_api.data_list_of_volunteers_at_event_with_patrol_boats.read(event_id), event_id=event_id)
        sql_identified_volunteers_at_event.write(csv_api.data_list_of_identified_volunteers_at_event.read(event_id), event_id=event_id)
        sql_list_of_volunteers_at_event.write(csv_api.data_list_of_volunteers_at_event.read(event_id), event_id=event_id)
        sql_identified_cadets_at_event.write(csv_api.data_identified_cadets_at_event.read(event_id), event_id=event_id)
        sql_event_warnings.write(csv_api.data_event_warnings.read(event_id), event_id=event_id)
        sql_mapped_registration_data.write(csv_api.data_registration_data.read(event_id), event_id=event_id)
        sql_field_mappings.write(csv_api.data_wa_field_mapping.read(event_id), event_id=event_id)

        sql_volunteers_with_roles.write(csv_api.data_list_of_volunteers_in_roles_at_event.read(event_id), event_id=event_id)

        list_of_cadets_with_groups = csv_api.data_list_of_cadets_with_groups.read(event_id)
        if len(list_of_cadets_with_groups)>0:
            sql_groups_at_events.write(list_of_cadets_with_groups, event_id)

        list_of_cadets_with_dinghies = csv_api.data_list_of_cadets_with_dinghies_at_event.read(event_id)
        sql_cadets_and_dinghies_at_event.write(list_of_cadets_with_dinghies, event_id=event_id)

        list_of_cadets_at_event = csv_api.data_cadets_at_event.read(event_id)
        sql_cadets_at_event.write(list_of_cadets_at_event, event_id=event_id)

        sql_club_dinghies_with_cadets.write(csv_api.data_list_of_cadets_at_event_with_club_dinghies.read(event_id), event_id=event_id)
        sql_club_dinghies_with_volunteers.write(csv_api.data_list_of_volunteers_at_event_with_club_dinghies.read(event_id), event_id=event_id)

    list_of_qualifications = csv_api.data_list_of_qualifications.read()
    sql_qualifications.write(list_of_qualifications)

    list_of_cadets_with_qualifications = csv_api.data_list_of_cadets_with_qualifications.read()
    sql_cadets_with_qualifications.write(list_of_cadets_with_qualifications)

    sql_cadets_on_committee.write(csv_api.data_list_of_cadets_on_committee.read())
    sql_list_of_volunteers.write(csv_api.data_list_of_volunteers.read())
    sql_associations.write(csv_api.data_list_of_cadet_volunteer_associations.read())
    sql_skills.write(csv_api.data_list_of_skills.read())
    sql_volunteers_with_skills.write(csv_api.data_list_of_volunteer_skills.read())
    sql_patrol_boats.write(csv_api.data_list_of_patrol_boats.read())

    sql_roles.write(csv_api.data_list_of_roles.read())
    sql_teams.write(csv_api.data_list_of_teams.read())
    sql_teams_and_roles.write(csv_api.data_list_of_teams_and_roles_with_ids.read())
    sql_event_mappings.write(csv_api.data_wa_event_mapping.read())
    sql_group_notes.write(csv_api.data_list_of_group_notes_at_event.read())
    sql_notes.write(csv_api.data_list_of_notes.read())
    sql_patrol_boat_labels.write(csv_api.data_list_of_patrol_boat_labels.read())
    sql_last_volunteer_roles.write(csv_api.data_list_of_last_roles_across_events_for_volunteers.read())

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
        csv_api.data_wa_field_mapping.write(sql_field_mappings.read(event_id), event_id=event_id)
        csv_api.data_event_warnings.write(sql_event_warnings.read(event_id), event_id=event_id)
        csv_api.data_identified_cadets_at_event.write(sql_identified_cadets_at_event.read(event_id), event_id=event_id)
        csv_api.data_list_of_volunteers_at_event.write(sql_list_of_volunteers_at_event.read(event_id), event_id=event_id)
        csv_api.data_list_of_identified_volunteers_at_event.write(sql_identified_volunteers_at_event.read(event_id), event_id=event_id)
        csv_api.data_list_of_volunteers_at_event_with_patrol_boats.write(sql_volunteers_with_patrol_boats.read(event_id=event_id), event_id=event_id)
        csv_api.data_list_of_targets_for_role_at_event.write(sql_targets_at_event.read(event_id), event_id=event_id)
        csv_api.data_list_of_cadets_with_food_requirement_at_event.write(sql_list_of_cadets_with_food_requirements.read(event_id=event_id), event_id=event_id)
        csv_api.data_list_of_volunteers_with_food_requirement_at_event.write(sql_list_of_volunteers_with_food_requirements.read(event_id), event_id=event_id)
        csv_api.data_list_of_cadets_with_clothing_at_event.write(sql_clothing.read(event_id=event_id), event_id=event_id)


    list_of_cadets = sql_cadets.read()

    for cadet in list_of_cadets:
        csv_api.data_attendance_at_events_for_specific_cadet.write(
            sql_attendance.read(cadet.id),
            cadet_id=cadet.id
        )
        csv_api.data_list_of_cadets_with_tick_list_items.write(
            sql_ticks.read(cadet.id),
            cadet_id=cadet.id
        )

    csv_api.data_list_of_cadets.write(list_of_cadets)

    csv_api.data_list_of_groups.write(sql_groups.read())

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
    csv_api.data_wa_event_mapping.write(sql_event_mappings.read())
    csv_api.data_List_of_club_dinghy_limits.write(sql_club_boat_limits.read())
    csv_api.data_list_of_tick_sub_stages.write(sql_substages.read())
    csv_api.data_list_of_tick_sheet_items.write(sql_tick_sheet_items.read())
    csv_api.data_list_of_group_notes_at_event.write(sql_group_notes.read())
    csv_api.data_list_of_notes.write(sql_notes.read())
    csv_api.data_list_of_patrol_boat_labels.write(sql_patrol_boat_labels.read())
    csv_api.data_list_of_last_roles_across_events_for_volunteers.write(sql_last_volunteer_roles.read())

    for report_name in ["Allocation report", "Patrol boat report", "Rollcall report", "Sailors with boats report", "Volunteer rota report"]:
        csv_api.data_arrangement_and_group_order_options.write(sql_arrangement_options.read(report_name), report_name=report_name)
        for default in ['', '_default']:
            full_name = "%s%s" % (report_name, default)
            csv_api.data_print_options.write(sql_print_options.read(full_name), report_name=full_name)

    list_of_templates = sql_template_field_mappings.list_of_template_names()
    for template_name in list_of_templates:
        csv_api.data_wa_field_mapping_templates.write(sql_template_field_mappings.read(template_name), template_name=template_name)



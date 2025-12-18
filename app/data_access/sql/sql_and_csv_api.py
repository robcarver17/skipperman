import shutil

from app.data_access.backups.make_backup import make_backup
from app.data_access.csv.cadets import *
from app.data_access.csv.food_and_clothing import *
from app.data_access.csv.global_read_only import (
    is_global_read_only,
    set_global_read_only,
)
from app.data_access.csv.wa_event_mapping import CsvDataWAEventMapping
from app.data_access.csv.wa_field_mapping import *
from app.data_access.csv.registration_data import *
from app.data_access.csv.configuration import *
from app.data_access.csv.volunteers import *
from app.data_access.csv.resources import *

from app.data_access.csv.users import CsvDataListOfSkipperManUsers
from app.data_access.csv.qualifications import *
from app.data_access.sql.cadet_committee import SqlDataListOfCadetsOnCommitte
from app.data_access.sql.cadets_at_event import SqlDataListOfCadetsAtEvent
from app.data_access.sql.club_dinghies import SqlDataListOfClubDinghies
from app.data_access.sql.connections import SqlDataListOfCadetVolunteerAssociations
from app.data_access.sql.dinghies_at_event import SqlDataListOfCadetAtEventWithDinghies
from app.data_access.sql.boat_classes import SqlDataListOfDinghies
from app.data_access.sql.events import SqlDataListOfEvents
from app.data_access.sql.generic_sql_data import DBConnection

from app.data_access.sql.groups import *
from app.data_access.sql.cadets import SqlDataListOfCadets
from app.data_access.sql.groups_at_event import SqlDataListOfCadetsWithGroups
from app.data_access.sql.list_of_roles_and_teams import SqlDataListOfTeamsAndRolesWithIds
from app.data_access.sql.patrol_boats import SqlDataListOfPatrolBoats
from app.data_access.sql.persistent_groups_at_events import SqlDataListOfGroupNamesForEventsAndCadetPersistentVersion
from app.data_access.sql.qualifications import SqlDataListOfQualifications
from app.data_access.sql.cadets_with_qualifications import SqlListOfCadetsWithQualifications
from app.data_access.sql.roles import SqlDataListOfRoles
from app.data_access.sql.skills import SqlDataListOfSkills
from app.data_access.sql.teams import SqlDataListOfTeams
from app.data_access.sql.volunteers import SqlDataListOfVolunteers
from app.data_access.sql.volunteers_in_roles_at_event import SqlDataListOfVolunteersInRolesAtEvent
from app.data_access.sql.volunteers_with_skills import SqlDataListOfVolunteerSkills


class MixedSqlAndCsvDataApi(object):
    def __init__(
        self, master_data_path: str, user_data_path: str, backup_data_path: str
    ):
        self._master_data_path = master_data_path
        self._user_data_path = user_data_path
        self._backup_data_path = backup_data_path

        db_connection =DBConnection(master_data_path)
        self._db_connection = db_connection

    @property
    def db_connection(self) -> DBConnection:
        return self._db_connection

    @property
    def global_read_only(self):
        return is_global_read_only(self.user_data_path)

    @global_read_only.setter
    def global_read_only(self, global_read_only: bool):
        set_global_read_only(self.user_data_path, global_read_only=global_read_only)

    def make_backup(self):
        make_backup(
            backup_data_path=self.backup_data_path,
            master_data_path=self.master_data_path,
        )

    @property
    def data_list_of_cadets(self):
        return SqlDataListOfCadets(
            self.db_connection
        )

    @property
    def data_list_of_cadets_on_committee(self) -> SqlDataListOfCadetsOnCommitte:
        return SqlDataListOfCadetsOnCommitte(
            self.db_connection
        )

    @property
    def data_list_of_events(self):
        return SqlDataListOfEvents(
            self.db_connection
        )

    @property
    def data_list_of_skills(self) -> SqlDataListOfSkills:
        return SqlDataListOfSkills(
            self.db_connection
        )

    @property
    def data_list_of_roles(self) -> SqlDataListOfRoles:
        return SqlDataListOfRoles(
            self.db_connection
        )

    @property
    def data_list_of_teams(self) -> SqlDataListOfTeams:
        return SqlDataListOfTeams(
            self.db_connection
        )

    @property
    def data_list_of_teams_and_roles_with_ids(
        self,
    ) -> SqlDataListOfTeamsAndRolesWithIds:
        return SqlDataListOfTeamsAndRolesWithIds(
            self.db_connection
        )

    @property
    def data_list_of_groups(self) -> SqlDataListOfGroups:
        return SqlDataListOfGroups(
            self.db_connection
        )

    @property
    def data_wa_event_mapping(self) -> CsvDataWAEventMapping:
        return CsvDataWAEventMapping(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_wa_field_mapping(self) -> CsvDataWAFieldMapping:
        return CsvDataWAFieldMapping(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_wa_field_mapping_templates(self) -> CsvDataWAFieldMappingTemplates:
        return CsvDataWAFieldMappingTemplates(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_wa_field_mapping_list_of_templates(self) -> CsvDataWAFieldMappingListOfTemplates:
        return CsvDataWAFieldMappingListOfTemplates(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_registration_data(self) -> CsvDataMappedRegistrationData:
        return CsvDataMappedRegistrationData(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_event_warnings(self) -> CsvDataListOfEventWarnings:
        return CsvDataListOfEventWarnings(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_identified_cadets_at_event(
        self,
    ) -> CsvDataListOfIdentifiedCadetsAtEvent:
        return CsvDataListOfIdentifiedCadetsAtEvent(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_cadets_at_event(
        self,
    ) -> SqlDataListOfCadetsAtEvent:
        return SqlDataListOfCadetsAtEvent(
            self.db_connection
        )

    @property
    def data_list_of_cadets_with_groups(
        self,
    ) -> SqlDataListOfCadetsWithGroups:
        return SqlDataListOfCadetsWithGroups(
            self.db_connection
        )

    @property
    def data_print_options(self) -> csvDataListOfPrintOptions:
        return csvDataListOfPrintOptions(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_arrangement_and_group_order_options(
        self,
    ) -> csvDataListOfArrangementOptions:
        return csvDataListOfArrangementOptions(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_volunteers(self) -> SqlDataListOfVolunteers:
        return SqlDataListOfVolunteers(
            self.db_connection
        )

    @property
    def data_list_of_volunteer_skills(self) -> SqlDataListOfVolunteerSkills:
        return SqlDataListOfVolunteerSkills(
            self.db_connection
        )

    @property
    def data_list_of_cadet_volunteer_associations(
        self,
    ) -> SqlDataListOfCadetVolunteerAssociations:
        return SqlDataListOfCadetVolunteerAssociations(
            self.db_connection
        )

    @property
    def data_list_of_volunteers_at_event(self) -> CsvDataListOfVolunteersAtEvent:
        return CsvDataListOfVolunteersAtEvent(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_identified_volunteers_at_event(
        self,
    ) ->CsvDataListOfIdentifiedVolunteersAtEvent:
        return CsvDataListOfIdentifiedVolunteersAtEvent(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_volunteers_in_roles_at_event(
        self,
    ) -> SqlDataListOfVolunteersInRolesAtEvent:
        return SqlDataListOfVolunteersInRolesAtEvent(
            self.db_connection
        )

    @property
    def data_list_of_patrol_boats(self) -> SqlDataListOfPatrolBoats:
        return SqlDataListOfPatrolBoats(
            self.db_connection
        )

    @property
    def data_List_of_club_dinghies(self) -> SqlDataListOfClubDinghies:
        return SqlDataListOfClubDinghies(
            self.db_connection
        )

    @property
    def data_List_of_club_dinghy_limits(self) -> CsvDataListOfClubDinghyLimits:
        return CsvDataListOfClubDinghyLimits(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )


    @property
    def data_list_of_group_names_for_events_and_cadets_persistent_version(self) -> SqlDataListOfGroupNamesForEventsAndCadetPersistentVersion:
        return SqlDataListOfGroupNamesForEventsAndCadetPersistentVersion(
            self.db_connection
        )

    @property
    def data_attendance_at_events_for_specific_cadet(
        self,
    ) -> CsvDataAttendanceAtEventsForSpecificCadet:
        return CsvDataAttendanceAtEventsForSpecificCadet(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_volunteers_at_event_with_patrol_boats(
        self,
    ) -> CsvDataListOfVolunteersAtEventWithPatrolBoats:
        return CsvDataListOfVolunteersAtEventWithPatrolBoats(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_cadets_at_event_with_club_dinghies(
        self,
    ) -> CsvDataListOfCadetAtEventWithClubDinghies:
        return CsvDataListOfCadetAtEventWithClubDinghies(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_volunteers_at_event_with_club_dinghies(
        self,
    ) -> CsvDataListOfVolunteersAtEventWithClubDinghies:
        return CsvDataListOfVolunteersAtEventWithClubDinghies(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_cadets_with_dinghies_at_event(
        self,
    ) -> SqlDataListOfCadetAtEventWithDinghies:
        return SqlDataListOfCadetAtEventWithDinghies(
            self.db_connection
        )

    @property
    def data_list_of_dinghies(self) -> SqlDataListOfDinghies:
        return SqlDataListOfDinghies(
            self.db_connection
        )

    @property
    def data_list_of_qualifications(self) -> SqlDataListOfQualifications:
        return SqlDataListOfQualifications(
            self.db_connection
        )

    @property
    def data_list_of_cadets_with_qualifications(
        self,
    ) -> SqlListOfCadetsWithQualifications:
        return SqlListOfCadetsWithQualifications(
            self.db_connection
        )

    @property
    def data_list_of_tick_sub_stages(self) -> CsvDataListOfTickSubStages:
        return CsvDataListOfTickSubStages(
            self.master_data_path, backup_data_path=self.backup_data_path
        )

    @property
    def data_list_of_tick_sheet_items(self) -> CsvDataListOfTickSheetItems:
        return CsvDataListOfTickSheetItems(
            self.master_data_path, backup_data_path=self.backup_data_path
        )

    @property
    def data_list_of_cadets_with_tick_list_items(
        self,
    ) -> CsvDataListOfCadetsWithTickListItems:
        return CsvDataListOfCadetsWithTickListItems(
            self.master_data_path, backup_data_path=self.backup_data_path
        )

    @property
    def data_list_of_targets_for_role_at_event(
        self,
    ) -> CsvDataListOfTargetForRoleAtEvent:
        return CsvDataListOfTargetForRoleAtEvent(
            self.master_data_path, backup_data_path=self.backup_data_path
        )

    @property
    def data_list_of_cadets_with_food_requirement_at_event(
        self,
    ) -> CsvDataListOfCadetsWithFoodRequirementsAtEvent:
        return CsvDataListOfCadetsWithFoodRequirementsAtEvent(
            self.master_data_path, backup_data_path=self.backup_data_path
        )

    @property
    def data_list_of_volunteers_with_food_requirement_at_event(
        self,
    ) -> CsvDataListOfVolunteersWithFoodRequirementsAtEvent:
        return CsvDataListOfVolunteersWithFoodRequirementsAtEvent(
            self.master_data_path, backup_data_path=self.backup_data_path
        )

    @property
    def data_list_of_cadets_with_clothing_at_event(
        self,
    ) -> CsvDataListOfCadetsWithClothingAtEvent:
        return CsvDataListOfCadetsWithClothingAtEvent(
            self.master_data_path, backup_data_path=self.backup_data_path
        )

    @property
    def data_list_of_group_notes_at_event(self) -> CsvDataListOfGroupNotesAtEvent:
        return CsvDataListOfGroupNotesAtEvent(
            self.master_data_path, backup_data_path=self.backup_data_path
        )

    @property
    def data_list_of_notes(self) -> CsvDataListOfNotes:
        return CsvDataListOfNotes(
            self.master_data_path, backup_data_path=self.backup_data_path
        )

    @property
    def data_list_of_patrol_boat_labels(self) -> CsvDataListOfPatrolBoatLabelsAtEvent:
        return CsvDataListOfPatrolBoatLabelsAtEvent(
            self.master_data_path, backup_data_path=self.backup_data_path
        )

    @property
    def data_list_of_last_roles_across_events_for_volunteers(self) -> CsvDataListOfLastRolesAcrossEventsForVolunteers:
        return CsvDataListOfLastRolesAcrossEventsForVolunteers(
            self.master_data_path, backup_data_path=self.backup_data_path
        )

    #### USERS

    @property
    def data_list_of_users(self) -> CsvDataListOfSkipperManUsers:
        return CsvDataListOfSkipperManUsers(
            self.user_data_path, backup_data_path=self.backup_data_path
        )

    ## PATHS

    @property
    def master_data_path(self) -> str:
        return self._master_data_path

    @property
    def user_data_path(self) -> str:
        return self._user_data_path

    @property
    def backup_data_path(self) -> str:
        return self._backup_data_path

    def delete_all_master_data(self, are_you_sure: bool = False):
        if are_you_sure:
            shutil.rmtree(self.master_data_path)

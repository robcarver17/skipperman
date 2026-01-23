import shutil

from app.data_access.backups.make_backup import make_backup
from app.data_access.csv.global_read_only import (
    is_global_read_only,
    set_global_read_only,
)

from app.data_access.csv.qualifications import CsvDataListOfCadetsWithTickListItems
from app.data_access.csv.arch.cadets import CsvDataAttendanceAtEventsForSpecificCadet
from app.data_access.csv.users import CsvDataListOfSkipperManUsers
from app.data_access.sql.cadet_attendance import SqlDataAttendanceAtEventsForSpecificCadet

from app.data_access.sql.cadet_clothing import SqlDataListOfCadetsWithClothingAtEvent
from app.data_access.sql.cadet_committee import SqlDataListOfCadetsOnCommitte
from app.data_access.sql.cadet_food import SqlDataListOfCadetsWithFoodRequirementsAtEvent
from app.data_access.sql.cadets_at_event import SqlDataListOfCadetsAtEvent
from app.data_access.sql.club_dinghies import SqlDataListOfClubDinghies
from app.data_access.sql.club_dinghies_with_people_at_event import SqlDataListOfCadetAtEventWithClubDinghies, \
    SqlDataListOfVolunteersAtEventWithClubDinghies
from app.data_access.sql.club_dinghy_limits import SqlDataListOfClubDinghyLimits
from app.data_access.sql.connections import SqlDataListOfCadetVolunteerAssociations
from app.data_access.sql.dinghies_at_event import SqlDataListOfCadetAtEventWithDinghies
from app.data_access.sql.boat_classes import SqlDataListOfDinghies
from app.data_access.sql.event_warnings import SqlDataListOfEventWarnings
from app.data_access.sql.events import SqlDataListOfEvents
from app.data_access.sql.field_mapping import SqlDataWAFieldMapping, SqlDataWAFieldMappingTemplates
from app.data_access.sql.generic_sql_data import DBConnection
from app.data_access.sql.group_notes import SqlDataListOfGroupNotesAtEvent

from app.data_access.sql.groups import SqlDataListOfGroups
from app.data_access.sql.cadets import SqlDataListOfCadets
from app.data_access.sql.groups_at_event import SqlDataListOfCadetsWithGroups
from app.data_access.sql.identified_cadets_at_event import SqlDataListOfIdentifiedCadetsAtEvent
from app.data_access.sql.identified_volunteers_at_event import SqlDataListOfIdentifiedVolunteersAtEvent
from app.data_access.sql.last_roles_across_events_for_volunteers import SqlDataListOfLastRolesAcrossEventsForVolunteers
from app.data_access.sql.list_of_roles_and_teams import SqlDataListOfTeamsAndRolesWithIds
from app.data_access.sql.mapped_registration_data import SqlDataMappedRegistrationData
from app.data_access.sql.notes import SqlDataListOfNotes
from app.data_access.sql.patrol_boat_labels import SqlDataListOfPatrolBoatLabelsAtEvent
from app.data_access.sql.patrol_boats import SqlDataListOfPatrolBoats
from app.data_access.sql.patrol_boats_with_volunteers_at_event import SqlDataListOfVolunteersAtEventWithPatrolBoats
from app.data_access.sql.persistent_groups_at_events import SqlDataListOfGroupNamesForEventsAndCadetPersistentVersion
from app.data_access.sql.print_options import sqlDataListOfPrintOptions, SqlDataListOfArrangementOptions
from app.data_access.sql.qualifications import SqlDataListOfQualifications
from app.data_access.sql.cadets_with_qualifications import SqlListOfCadetsWithQualifications
from app.data_access.sql.roles import SqlDataListOfRoles
from app.data_access.sql.skills import SqlDataListOfSkills
from app.data_access.sql.target_roles_at_event import SqlDataListOfTargetForRoleAtEvent
from app.data_access.sql.teams import SqlDataListOfTeams
from app.data_access.sql.tick_sheet_items import SqlDataListOfTickSheetItems
from app.data_access.sql.tick_sheet_sub_stages import SqlDataListOfTickSubStages
from app.data_access.sql.volunteer_food import SqlDataListOfVolunteersWithFoodRequirementsAtEvent
from app.data_access.sql.volunteers import SqlDataListOfVolunteers
from app.data_access.sql.volunteers_at_event import SqlDataListOfVolunteersAtEvent
from app.data_access.sql.volunteers_in_roles_at_event import SqlDataListOfVolunteersInRolesAtEvent
from app.data_access.sql.volunteers_with_skills import SqlDataListOfVolunteerSkills
from app.data_access.sql.wa_event_mapping import SqlDataWAEventMapping

#FIXME PROBABLY SOME CLEANUP HERE

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
    def data_wa_event_mapping(self) -> SqlDataWAEventMapping:
        return SqlDataWAEventMapping(
            self.db_connection
        )

    @property
    def data_wa_field_mapping(self) -> SqlDataWAFieldMapping:
        return SqlDataWAFieldMapping(
            self.db_connection
        )

    @property
    def data_wa_field_mapping_templates(self) -> SqlDataWAFieldMappingTemplates:
        return SqlDataWAFieldMappingTemplates(
            self.db_connection
        )


    @property
    def data_registration_data(self) -> SqlDataMappedRegistrationData:
        return SqlDataMappedRegistrationData(
            self.db_connection
        )

    @property
    def data_event_warnings(self) -> SqlDataListOfEventWarnings:
        return SqlDataListOfEventWarnings(
            self.db_connection
        )

    @property
    def data_identified_cadets_at_event(
        self,
    ) -> SqlDataListOfIdentifiedCadetsAtEvent:
        return SqlDataListOfIdentifiedCadetsAtEvent(
            self.db_connection
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
    def data_print_options(self) -> sqlDataListOfPrintOptions:
        return sqlDataListOfPrintOptions(
            self.db_connection
        )

    @property
    def data_arrangement_and_group_order_options(
        self,
    ) -> SqlDataListOfArrangementOptions:
        return SqlDataListOfArrangementOptions(
            self.db_connection
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
    def data_list_of_volunteers_at_event(self) -> SqlDataListOfVolunteersAtEvent:
        return SqlDataListOfVolunteersAtEvent(
        self.db_connection
        )

    @property
    def data_list_of_identified_volunteers_at_event(
        self,
    ) ->SqlDataListOfIdentifiedVolunteersAtEvent:
        return SqlDataListOfIdentifiedVolunteersAtEvent(
            self.db_connection
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
    def data_List_of_club_dinghy_limits(self) -> SqlDataListOfClubDinghyLimits:
        return SqlDataListOfClubDinghyLimits(
            self.db_connection
        )


    @property
    def data_list_of_group_names_for_events_and_cadets_persistent_version(self) -> SqlDataListOfGroupNamesForEventsAndCadetPersistentVersion:
        return SqlDataListOfGroupNamesForEventsAndCadetPersistentVersion(
            self.db_connection
        )

    @property
    def data_attendance_at_events_for_specific_cadet(
        self,
    ) -> SqlDataAttendanceAtEventsForSpecificCadet:
        return SqlDataAttendanceAtEventsForSpecificCadet(
            self.db_connection
        )

    @property
    def data_list_of_volunteers_at_event_with_patrol_boats(
        self,
    ) -> SqlDataListOfVolunteersAtEventWithPatrolBoats:
        return SqlDataListOfVolunteersAtEventWithPatrolBoats(
            self.db_connection
        )

    @property
    def data_list_of_cadets_at_event_with_club_dinghies(
        self,
    ) -> SqlDataListOfCadetAtEventWithClubDinghies:
        return SqlDataListOfCadetAtEventWithClubDinghies(
            self.db_connection
        )

    @property
    def data_list_of_volunteers_at_event_with_club_dinghies(
        self,
    ) -> SqlDataListOfVolunteersAtEventWithClubDinghies:
        return SqlDataListOfVolunteersAtEventWithClubDinghies(
            self.db_connection
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
    def data_list_of_tick_sub_stages(self) -> SqlDataListOfTickSubStages:
        return SqlDataListOfTickSubStages(
            self.db_connection
        )

    @property
    def data_list_of_tick_sheet_items(self) -> SqlDataListOfTickSheetItems:
        return SqlDataListOfTickSheetItems(
            self.db_connection
        )

    ## KEEP AS CSV
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
    ) -> SqlDataListOfTargetForRoleAtEvent:
        return SqlDataListOfTargetForRoleAtEvent(
            self.db_connection
        )

    @property
    def data_list_of_cadets_with_food_requirement_at_event(
        self,
    ) -> SqlDataListOfCadetsWithFoodRequirementsAtEvent:
        return SqlDataListOfCadetsWithFoodRequirementsAtEvent(
            self.db_connection
        )

    @property
    def data_list_of_volunteers_with_food_requirement_at_event(
        self,
    ) -> SqlDataListOfVolunteersWithFoodRequirementsAtEvent:
        return SqlDataListOfVolunteersWithFoodRequirementsAtEvent(
            self.db_connection
        )

    @property
    def data_list_of_cadets_with_clothing_at_event(
        self,
    ) -> SqlDataListOfCadetsWithClothingAtEvent:
        return SqlDataListOfCadetsWithClothingAtEvent(
        self.db_connection
        )

    @property
    def data_list_of_group_notes_at_event(self) -> SqlDataListOfGroupNotesAtEvent:
        return SqlDataListOfGroupNotesAtEvent(
            self.db_connection
        )

    @property
    def data_list_of_notes(self) ->SqlDataListOfNotes:
        return SqlDataListOfNotes(
        self.db_connection
        )

    @property
    def data_list_of_patrol_boat_labels(self) -> SqlDataListOfPatrolBoatLabelsAtEvent:
        return SqlDataListOfPatrolBoatLabelsAtEvent(
            self.db_connection
        )

    @property
    def data_list_of_last_roles_across_events_for_volunteers(self) ->SqlDataListOfLastRolesAcrossEventsForVolunteers:
        return SqlDataListOfLastRolesAcrossEventsForVolunteers(
self.db_connection
        )

    #### USERS
    ## KEEP AS CSV
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

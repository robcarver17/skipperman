import shutil

from app.data_access.backups.make_backup import make_backup
from app.data_access.csv.cadets import *
from app.data_access.csv.food_and_clothing import *
from app.data_access.csv.global_read_only import (
    is_global_read_only,
    set_global_read_only,
)
from app.data_access.csv.list_of_events import CsvDataListOfEvents
from app.data_access.csv.wa_event_mapping import CsvDataWAEventMapping
from app.data_access.csv.wa_field_mapping import *
from app.data_access.csv.registration_data import *
from app.data_access.csv.configuration import *
from app.data_access.csv.volunteers import *
from app.data_access.csv.resources import *
from app.data_access.csv.dinghies_at_events import (
    CsvDataListOfCadetAtEventWithDinghies,
    CsvDataListOfDinghies,
)
from app.data_access.csv.users import CsvDataListOfSkipperManUsers
from app.data_access.csv.qualifications import *


class CsvDataApi(object):
    def __init__(
        self, master_data_path: str, user_data_path: str, backup_data_path: str
    ):
        self._master_data_path = master_data_path
        self._user_data_path = user_data_path
        self._backup_data_path = backup_data_path

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
        return CsvDataListOfCadets(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_cadets_on_committee(self) -> CsvDataListOfCadetsOnCommitte:
        return CsvDataListOfCadetsOnCommitte(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_events(self):
        return CsvDataListOfEvents(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_skills(self) -> CsvDataListOfSkills:
        return CsvDataListOfSkills(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_roles(self) -> CsvDataListOfRoles:
        return CsvDataListOfRoles(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_teams(self) -> CsvDataListOfTeams:
        return CsvDataListOfTeams(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_teams_and_roles_with_ids(
        self,
    ) -> CsvDataListOfTeamsAndRolesWithIds:
        return CsvDataListOfTeamsAndRolesWithIds(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_groups(self) -> csvDataListOfGroups:
        return csvDataListOfGroups(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
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
    ) -> CsvDataListOfCadetsAtEvent:
        return CsvDataListOfCadetsAtEvent(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_cadets_with_groups(
        self,
    ) -> CsvDataListOfCadetsWithGroups:
        return CsvDataListOfCadetsWithGroups(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
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
    def data_list_of_volunteers(self) -> CsvDataListOfVolunteers:
        return CsvDataListOfVolunteers(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_volunteer_skills(self) -> CsvDataListOfVolunteerSkills:
        return CsvDataListOfVolunteerSkills(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_cadet_volunteer_associations(
        self,
    ) -> CsvDataListOfCadetVolunteerAssociations:
        return CsvDataListOfCadetVolunteerAssociations(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
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
    ) -> CsvDataListOfVolunteersInRolesAtEvent:
        return CsvDataListOfVolunteersInRolesAtEvent(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_patrol_boats(self) -> CsvDataListOfPatrolBoats:
        return CsvDataListOfPatrolBoats(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_List_of_club_dinghies(self) -> CsvDataListOfClubDinghies:
        return CsvDataListOfClubDinghies(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_List_of_club_dinghy_limits(self) -> CsvDataListOfClubDinghyLimits:
        return CsvDataListOfClubDinghyLimits(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
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
    ) -> CsvDataListOfCadetAtEventWithDinghies:
        return CsvDataListOfCadetAtEventWithDinghies(
            master_data_path=self.master_data_path,
            backup_data_path=self.backup_data_path,
        )

    @property
    def data_list_of_dinghies(self) -> CsvDataListOfDinghies:
        return CsvDataListOfDinghies(
            self.master_data_path, backup_data_path=self.backup_data_path
        )

    @property
    def data_list_of_qualifications(self) -> CsvDataListOfQualifications:
        return CsvDataListOfQualifications(
            self.master_data_path, backup_data_path=self.backup_data_path
        )

    @property
    def data_list_of_cadets_with_qualifications(
        self,
    ) -> CsvListOfCadetsWithQualifications:
        return CsvListOfCadetsWithQualifications(
            self.master_data_path, backup_data_path=self.backup_data_path
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

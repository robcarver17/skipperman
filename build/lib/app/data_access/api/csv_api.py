from app.data_access.api.generic_api import GenericDataApi
from app.data_access.csv.master_list_of_cadets import CsvDataListOfCadets
from app.data_access.csv.list_of_events import CsvDataListOfEvents
from app.data_access.csv.wa_event_mapping import CsvDataWAEventMapping
from app.data_access.csv.wa_field_mapping import CsvDataWAFieldMapping
from app.data_access.csv.mapped_wa_event import (
    CsvDataMappedWAEventWithNoIDs,
    CsvDataMappedWAEventWithIDs,
    CsvDataMasterEvent,
)
from app.data_access.csv.cadets_with_groups_for_event import (
    CsvDataListOfCadetsWithGroups,
)
from app.data_access.csv.print_options import csvDataListOfPrintOptions
from app.data_access.csv.volunteers import CsvDataListOfVolunteers, CsvDataListOfVolunteerSkills, CsvDataListOfCadetVolunteerAssociations, CsvDataListOfVolunteersAtEvent, CsvDataListOfCadetsWithoutVolunteersAtEvent, CsvDataListOfVolunteersInRolesAtEvent
from app.data_access.csv.resources import *

class CsvDataApi(GenericDataApi):
    def __init__(self, master_data_path: str):
        self._master_data_path = master_data_path

    @property
    def data_list_of_cadets(self):
        return CsvDataListOfCadets(master_data_path=self.master_data_path)

    @property
    def data_list_of_events(self):
        return CsvDataListOfEvents(master_data_path=self.master_data_path)

    @property
    def data_wa_event_mapping(self) -> CsvDataWAEventMapping:
        return CsvDataWAEventMapping(master_data_path=self.master_data_path)

    @property
    def data_wa_field_mapping(self) -> CsvDataWAFieldMapping:
        return CsvDataWAFieldMapping(master_data_path=self.master_data_path)

    @property
    def data_mapped_wa_event_with_no_ids(self) -> CsvDataMappedWAEventWithNoIDs:
        return CsvDataMappedWAEventWithNoIDs(master_data_path=self.master_data_path)

    @property
    def data_mapped_wa_event_with_cadet_ids(self) -> CsvDataMappedWAEventWithIDs:
        return CsvDataMappedWAEventWithIDs(master_data_path=self.master_data_path)

    @property
    def data_master_event(
        self,
    ) -> CsvDataMasterEvent:
        return CsvDataMasterEvent(master_data_path=self.master_data_path)

    @property
    def data_list_of_cadets_with_groups(
        self,
    ) -> CsvDataListOfCadetsWithGroups:
        return CsvDataListOfCadetsWithGroups(master_data_path=self.master_data_path)

    @property
    def data_print_options(self) -> csvDataListOfPrintOptions:
        return csvDataListOfPrintOptions(master_data_path=self.master_data_path)

    @property
    def master_data_path(self) -> str:
        return self._master_data_path

    @property
    def data_list_of_volunteers(self) -> CsvDataListOfVolunteers:
        return CsvDataListOfVolunteers(master_data_path=self.master_data_path)

    @property
    def data_list_of_volunteer_skills(self) -> CsvDataListOfVolunteerSkills:
        return CsvDataListOfVolunteerSkills(master_data_path=self.master_data_path)

    @property
    def data_list_of_cadet_volunteer_associations(self) -> CsvDataListOfCadetVolunteerAssociations:
        return CsvDataListOfCadetVolunteerAssociations(master_data_path=self.master_data_path)

    @property
    def data_list_of_volunteers_at_event(self) -> CsvDataListOfVolunteersAtEvent:
        return CsvDataListOfVolunteersAtEvent(master_data_path=self.master_data_path)

    @property
    def data_list_of_cadets_without_volunteers_at_event(self) -> CsvDataListOfCadetsWithoutVolunteersAtEvent:
        return CsvDataListOfCadetsWithoutVolunteersAtEvent(master_data_path=self.master_data_path)

    @property
    def data_list_of_volunteers_in_roles_at_event(self) -> CsvDataListOfVolunteersInRolesAtEvent:
        return CsvDataListOfVolunteersInRolesAtEvent(master_data_path=self.master_data_path)

    @property
    def data_list_of_patrol_boats(self) -> CsvDataListOfPatrolBoats:
        return CsvDataListOfPatrolBoats(master_data_path=self.master_data_path)

    @property
    def data_List_of_club_dinghies(self) -> CsvDataListOfClubDinghies:
        return CsvDataListOfClubDinghies(master_data_path=self.master_data_path)

    @property
    def data_list_of_volunteers_at_event_with_patrol_boats(self) -> CsvDataListOfVolunteersAtEventWithPatrolBoats:
        return CsvDataListOfVolunteersAtEventWithPatrolBoats(master_data_path=self.master_data_path)

    @property
    def data_list_of_volunteers_at_event_with_club_dinghies(self) -> CsvDataListOfCadetAtEventWithClubDinghies:
        return CsvDataListOfCadetAtEventWithClubDinghies(master_data_path=self.master_data_path)
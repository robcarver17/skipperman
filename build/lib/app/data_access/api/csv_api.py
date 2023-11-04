from app.data_access.api.generic_api import GenericDataApi
from app.data_access.csv.master_list_of_cadets import CsvDataListOfCadets
from app.data_access.csv.list_of_events import CsvDataListOfEvents
from app.data_access.csv.wa_event_mapping import CsvDataWAEventMapping
from app.data_access.csv.wa_field_mapping import CsvDataWAFieldMapping
from app.data_access.csv.mapped_wa_event import (
    CsvDataMappedWAEventWithNoIDs,
    CsvDataMappedWAEventWithIDs,
    CsvDataMappedWAEventWithoutDuplicatesAndWithStatus,
)
from app.data_access.csv.cadets_with_groups_for_event import (
    CsvDataListOfCadetsWithGroups,
)


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
    def data_mapped_wa_event_without_duplicates_and_with_status(
        self,
    ) -> CsvDataMappedWAEventWithoutDuplicatesAndWithStatus:
        return CsvDataMappedWAEventWithoutDuplicatesAndWithStatus(
            master_data_path=self.master_data_path
        )

    @property
    def data_list_of_cadets_with_groups(
        self,
    ) -> CsvDataListOfCadetsWithGroups:
        return CsvDataListOfCadetsWithGroups(master_data_path=self.master_data_path)

    @property
    def master_data_path(self) -> str:
        return self._master_data_path

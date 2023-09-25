from data_access.api.generic_api import GenericDataApi
from data_access.csv.master_list_of_cadets import CsvDataListOfCadets
from data_access.csv.list_of_events import CsvDataListOfEvents
from data_access.csv.wa_event_mapping import CsvDataWAEventMapping
from data_access.csv.wa_field_mapping import CsvDataWAFieldMapping
from data_access.csv.mapped_wa_event import CsvDataMappedWAEvent

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
    def master_data_path(self) -> str:
        return self._master_data_path

    @property
    def data_wa_event_mapping(self) -> CsvDataWAEventMapping:
        return CsvDataWAEventMapping(master_data_path=self.master_data_path)

    @property
    def data_wa_field_mapping(self) -> CsvDataWAFieldMapping:
        return CsvDataWAFieldMapping(master_data_path=self.master_data_path)

    def data_mapped_wa_event(self) -> CsvDataMappedWAEvent:
        return CsvDataMappedWAEvent(master_data_path=self.master_data_path)
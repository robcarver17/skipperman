import pandas as pd
from app.data_access.csv.generic_csv_data import GenericCsvData
from app.objects.wa_event_mapping import ListOfWAEventMaps
from app.data_access.classes.wa_event_mapping import DataWAEventMapping

EVENT_MAPPING_FILE_ID = "wa_event_mapping"

class CsvDataWAEventMapping(GenericCsvData, DataWAEventMapping):
    def read(self) -> ListOfWAEventMaps:
        wa_event_mapping = self.read_and_return_object_of_type(ListOfWAEventMaps, file_identifier=EVENT_MAPPING_FILE_ID)

        return wa_event_mapping

    def write(self, wa_event_mapping: ListOfWAEventMaps):
        self.write_object(wa_event_mapping, file_identifier=EVENT_MAPPING_FILE_ID)



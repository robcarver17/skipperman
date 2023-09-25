import pandas as pd
from data_access.csv.generic_csv_data import GenericCsvData
from objects.mapped_wa_event import MappedWAEvent
from data_access.classes.mapped_wa_event import DataMappedWAEvent

class CsvDataMappedWAEvent(GenericCsvData, DataMappedWAEvent):
    def read(self, event_id: str) -> MappedWAEvent:
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        mapped_wa_event_df = pd.read_csv(path_and_filename)
        ## error condition for mssing file
        mapped_wa_event = MappedWAEvent.from_df(mapped_wa_event_df)

        return mapped_wa_event

    def write(self, event_id: str,  mapped_wa_event: MappedWAEvent):
        df = mapped_wa_event.to_df()
        path_and_filename = self.path_and_filename_for_eventid(event_id)

        df.to_csv(path_and_filename, index=False)

    def path_and_filename_for_eventid(self, event_id: str):
        return self.get_path_and_filename_for_named_csv_file("mapped_wa_event",
                                                             additional_file_identifiers=event_id)

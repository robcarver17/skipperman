import pandas as pd
from app.data_access.csv.generic_csv_data import GenericCsvData
from app.data_access.csv.resolve_csv_paths_and_filenames import MAPPED_WA_EVENT_FILE_ID
from app.objects.utils import transform_df_from_dates_to_str, transform_df_from_str_to_dates

from app.objects.mapped_wa_event import MappedWAEvent
from app.data_access.classes.mapped_wa_event import (
    DataMappedWAEvent,
)


class CsvDataMappedWAEvent(GenericCsvData, DataMappedWAEvent):
    def read(self, event_id: str) -> MappedWAEvent:
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        try:
            mapped_wa_event_df = pd.read_csv(path_and_filename)
        except FileNotFoundError:
            return MappedWAEvent.create_empty()

        transform_df_from_str_to_dates(mapped_wa_event_df)
        mapped_wa_event = MappedWAEvent.from_df(mapped_wa_event_df)

        return mapped_wa_event

    def write(self, mapped_wa_event: MappedWAEvent, event_id: str):
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        if len(mapped_wa_event) == 0:
            self.delete(path_and_filename)
        else:
            df = mapped_wa_event.to_df()
            transform_df_from_dates_to_str(df)

            df.to_csv(path_and_filename, index=False)

    def path_and_filename_for_eventid(self, event_id: str):
        return self.get_path_and_filename_for_named_csv_file(
            MAPPED_WA_EVENT_FILE_ID, additional_file_identifiers=event_id
        )



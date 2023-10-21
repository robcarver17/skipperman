import pandas as pd
from app.data_access import GenericCsvData
from app.data_access import (
    transform_df_from_str_to_dates,
    transform_df_from_dates_to_str,
)
from app.objects import (
    MappedWAEventWithoutDuplicatesAndWithStatus,
)
from app.objects import MappedWAEventWithIDs
from app.data_access import (
    DataMappedWAEventWithIDs,
    DataMappedWAEventWithoutDuplicatesAndWithStatus,
)


class CsvDataMappedWAEventWithIDs(GenericCsvData, DataMappedWAEventWithIDs):
    def read(self, event_id: str) -> MappedWAEventWithIDs:
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        try:
            mapped_wa_event_df = pd.read_csv(path_and_filename)
        except FileNotFoundError:
            return MappedWAEventWithIDs.create_empty()

        transform_df_from_str_to_dates(mapped_wa_event_df)
        mapped_wa_event = MappedWAEventWithIDs.from_df(mapped_wa_event_df)

        return mapped_wa_event

    def write(self, event_id: str, mapped_wa_event_with_ids: MappedWAEventWithIDs):
        df = mapped_wa_event_with_ids.to_df()
        transform_df_from_dates_to_str(df)
        path_and_filename = self.path_and_filename_for_eventid(event_id)

        df.to_csv(path_and_filename, index=False)

    def path_and_filename_for_eventid(self, event_id: str):
        return self.get_path_and_filename_for_named_csv_file(
            "mapped_wa_event_with_ids", additional_file_identifiers=event_id
        )


class CsvDataMappedWAEventWithoutDuplicatesAndWithStatus(
    GenericCsvData, DataMappedWAEventWithoutDuplicatesAndWithStatus
):
    def read(self, event_id: str) -> MappedWAEventWithoutDuplicatesAndWithStatus:
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        try:
            mapped_wa_event_df = pd.read_csv(path_and_filename)
        except FileNotFoundError:
            return MappedWAEventWithoutDuplicatesAndWithStatus.create_empty()

        transform_df_from_str_to_dates(mapped_wa_event_df)
        mapped_wa_event = MappedWAEventWithoutDuplicatesAndWithStatus.from_df(
            mapped_wa_event_df
        )

        return mapped_wa_event

    def write(
        self,
        event_id: str,
        mapped_wa_event_without_duplicates: MappedWAEventWithoutDuplicatesAndWithStatus,
    ):
        df = mapped_wa_event_without_duplicates.to_df()
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        transform_df_from_dates_to_str(df)

        df.to_csv(path_and_filename, index=False)

    def path_and_filename_for_eventid(self, event_id: str):
        return self.get_path_and_filename_for_named_csv_file(
            "mapped_wa_event_without_duplicates_and_with_status",
            additional_file_identifiers=event_id,
        )

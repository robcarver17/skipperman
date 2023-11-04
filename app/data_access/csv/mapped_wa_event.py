import pandas as pd
from app.data_access.csv.generic_csv_data import GenericCsvData
from app.data_access.csv.utils import (
    transform_df_from_str_to_dates,
    transform_df_from_dates_to_str,
)
from app.objects.mapped_wa_event_with_id_and_status import (
    MappedWAEventWithoutDuplicatesAndWithStatus,
)
from app.objects.mapped_wa_event_no_ids import MappedWAEventNoIDs
from app.objects.mapped_wa_event_with_ids import MappedWAEventWithIDs
from app.data_access.classes.mapped_wa_event import (
    DataMappedWAEventWithNoIDs,
    DataMappedWAEventWithIDs,
    DataMappedWAEventWithoutDuplicatesAndWithStatus,
)


class CsvDataMappedWAEventWithNoIDs(GenericCsvData, DataMappedWAEventWithNoIDs):
    def read(self, event_id: str) -> MappedWAEventNoIDs:
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        try:
            mapped_wa_event_df = pd.read_csv(path_and_filename)
        except FileNotFoundError:
            return MappedWAEventNoIDs.create_empty()

        transform_df_from_str_to_dates(mapped_wa_event_df)
        mapped_wa_event = MappedWAEventNoIDs.from_df(mapped_wa_event_df)

        return mapped_wa_event

    def write(self, mapped_wa_event_with_no_ids: MappedWAEventNoIDs, event_id: str):
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        if len(mapped_wa_event_with_no_ids) == 0:
            self.delete(path_and_filename)
        else:
            df = mapped_wa_event_with_no_ids.to_df()
            transform_df_from_dates_to_str(df)

            df.to_csv(path_and_filename, index=False)

    def path_and_filename_for_eventid(self, event_id: str):
        return self.get_path_and_filename_for_named_csv_file(
            "mapped_wa_event_with_no_ids", additional_file_identifiers=event_id
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
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        if len(mapped_wa_event_with_ids) == 0:
            self.delete(path_and_filename)
        else:
            df = mapped_wa_event_with_ids.to_df()
            transform_df_from_dates_to_str(df)

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
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        if len(mapped_wa_event_without_duplicates) == 0:
            self.delete(path_and_filename)
        else:
            df = mapped_wa_event_without_duplicates.to_df()
            transform_df_from_dates_to_str(df)

            df.to_csv(path_and_filename, index=False)

    def path_and_filename_for_eventid(self, event_id: str):
        return self.get_path_and_filename_for_named_csv_file(
            "mapped_wa_event_without_duplicates_and_with_status",
            additional_file_identifiers=event_id,
        )

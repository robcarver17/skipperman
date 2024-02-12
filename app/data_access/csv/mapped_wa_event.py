import pandas as pd
from app.data_access.csv.generic_csv_data import GenericCsvData
from app.objects.utils import transform_df_to_str, transform_df_from_dates_to_str, transform_df_from_str_to_dates
from app.objects.master_event import (
    MasterEvent,
)
from app.objects.mapped_wa_event import MappedWAEvent
from app.objects.mapped_wa_event_deltas import MappedWAEventListOfDeltaRows
from app.data_access.classes.mapped_wa_event import (
    DataMappedWAEvent,
    DataMappedWAEventDeltaRows,
    DataMasterEvent,
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

    def write(self, mapped_wa_event_with_no_ids: MappedWAEvent, event_id: str):
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        if len(mapped_wa_event_with_no_ids) == 0:
            self.delete(path_and_filename)
        else:
            df = mapped_wa_event_with_no_ids.to_df()
            transform_df_from_dates_to_str(df)

            df.to_csv(path_and_filename, index=False)

    def path_and_filename_for_eventid(self, event_id: str):
        return self.get_path_and_filename_for_named_csv_file(
            "mapped_wa_event", additional_file_identifiers=event_id
        )


class CsvDataMappedWAEventWithDeltaRows(GenericCsvData, DataMappedWAEventDeltaRows):
    def read(self, event_id: str) -> MappedWAEventListOfDeltaRows:
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        try:
            mapped_wa_event_df = pd.read_csv(path_and_filename)
        except FileNotFoundError:
            return MappedWAEventListOfDeltaRows.create_empty()

        transform_df_from_str_to_dates(mapped_wa_event_df)
        transform_df_to_str(mapped_wa_event_df)

        mapped_wa_event = MappedWAEventListOfDeltaRows.from_df(mapped_wa_event_df)

        return mapped_wa_event

    def write(self, event_id: str, mapped_wa_event_with_ids: MappedWAEventListOfDeltaRows):
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        if len(mapped_wa_event_with_ids) == 0:
            self.delete(path_and_filename)
        else:
            df = mapped_wa_event_with_ids.to_df()
            transform_df_from_dates_to_str(df)

            df.to_csv(path_and_filename, index=False)

    def path_and_filename_for_eventid(self, event_id: str):
        return self.get_path_and_filename_for_named_csv_file(
            "mapped_wa_event_delta_rows", additional_file_identifiers=event_id
        )


class CsvDataMasterEvent(GenericCsvData, DataMasterEvent):
    def read(self, event_id: str) -> MasterEvent:
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        try:
            mapped_wa_event_df = pd.read_csv(path_and_filename)
        except FileNotFoundError:
            return MasterEvent.create_empty()

        transform_df_from_str_to_dates(mapped_wa_event_df)
        transform_df_to_str(mapped_wa_event_df)

        mapped_wa_event = MasterEvent.from_df(mapped_wa_event_df)

        return mapped_wa_event

    def write(
        self,
        event_id: str,
        master_event: MasterEvent,
    ):
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        if len(master_event) == 0:
            self.delete(path_and_filename)
        else:
            df = master_event.to_df()
            transform_df_from_dates_to_str(df)

            df.to_csv(path_and_filename, index=False)

    def path_and_filename_for_eventid(self, event_id: str):
        return self.get_path_and_filename_for_named_csv_file(
            "master_event",
            additional_file_identifiers=event_id,
        )

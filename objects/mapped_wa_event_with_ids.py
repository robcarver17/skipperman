import datetime
from dataclasses import dataclass
from typing import List

import pandas as pd

from objects.constants import missing_data
from objects.mapped_wa_event_no_ids import (
    RowInMappedWAEventNoId,
    MappedWAEventNoIDs,
    extract_list_of_entry_timestamps_from_existing_wa_event,
)

CADET_ID = "cadet_id"


@dataclass
class RowInMappedWAEventWithId:
    cadet_id: str
    data_in_row: RowInMappedWAEventNoId

    def get_data_attribute_or_missing_data(self, attr_name: str):
        return self.data_in_row.get(attr_name, missing_data)

    def as_dict(self):
        data_in_row_as_dict = dict(self.data_in_row)
        data_in_row_as_dict.update({CADET_ID: self.cadet_id})

        return data_in_row_as_dict

    @classmethod
    def from_dict(cls, some_dict: dict):
        cadet_id = some_dict.pop(CADET_ID)

        return cls(
            cadet_id=cadet_id,
            data_in_row=RowInMappedWAEventNoId.from_external_dict(some_dict),
        )

    @property
    def registration_date(self) -> datetime.datetime:
        return self.data_in_row.registration_date


class MappedWAEventWithIDs(list):
    def __init__(self, list_of_rows: List[RowInMappedWAEventWithId]):
        super().__init__(list_of_rows)

    def __repr__(self):
        return str(self.to_df())

    def list_of_timestamps(self) -> list:
        ## ignore type warning works
        return extract_list_of_entry_timestamps_from_existing_wa_event(self)

    def update_data_in_row_with_timestamp(self, data: dict, timestamp):
        current_row = self.get_row_with_timestamp(timestamp)
        current_row.data_in_row = data

    def add_new_rows(self, list_of_rows: "MappedWAEventWithIDs"):
        ## new rows should be on top eg first
        [self.add_row(new_row) for new_row in list_of_rows]

    def add_row(self, new_row: RowInMappedWAEventWithId):
        self.insert(0, new_row)

    def delete_list_of_rows_with_timestamps(self, list_of_timestamps: list):
        [self.delete_row_with_timetsamps(timestamp) for timestamp in list_of_timestamps]

    def delete_row_with_timetsamps(self, timestamp):
        list_of_timestamps = self.list_of_timestamps()
        try:
            idx = list_of_timestamps.index(timestamp)
        except:
            raise Exception(
                "Can't delete non existing row with timestamp %s" % str(timestamp)
            )

        self.pop(idx)

    @classmethod
    def from_df(cls, some_df: pd.DataFrame):
        list_of_dicts = [
            RowInMappedWAEventWithId.from_dict(df_row.to_dict())
            for __, df_row in some_df.iterrows()
        ]
        return cls(list_of_dicts)

    def to_df(self) -> pd.DataFrame:
        list_of_dicts = [item.as_dict() for item in self]

        return pd.DataFrame(list_of_dicts)

    @classmethod
    def from_unmapped_event_and_id_list(
        cls, mapped_event_no_ids: MappedWAEventNoIDs, list_of_cadet_ids: list
    ):
        mapped_event_with_ids = [
            RowInMappedWAEventWithId(cadet_id=cadet_id, data_in_row=mapped_event_row)
            for cadet_id, mapped_event_row in zip(
                list_of_cadet_ids, mapped_event_no_ids
            )
        ]

        return cls(mapped_event_with_ids)

    def get_row_with_timestamp(self, timestamp):
        list_of_timestamps = self.list_of_timestamps()
        try:
            idx_of_timestamp = list_of_timestamps.index(timestamp)
        except ValueError:
            raise Exception("Timestamp %s not found in data" % str(timestamp))

        return self[idx_of_timestamp]

    def get_row_with_id(self, cadet_id: str):
        try:
            matching_row = self[self.list_of_cadet_ids.index(cadet_id)]
        except ValueError:
            raise Exception("Cadet id %s not in data" % cadet_id)

        return matching_row

    def is_cadet_id_in_event(self, cadet_id: str) -> bool:
        return cadet_id in self.list_of_cadet_ids

    @property
    def list_of_cadet_ids(self) -> list:
        return [row.cadet_id for row in self]

    @classmethod
    def create_empty(cls):
        return cls([])

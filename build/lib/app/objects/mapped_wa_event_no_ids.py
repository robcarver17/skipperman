from typing import List
import pandas as pd

from app.objects.utils import (
    clean_up_dict_with_nans,
    transform_df_from_str_to_dates
)

from app.data_access.configuration.field_list import REGISTRATION_DATE


# can't use generic methods here as based on dataclasses
class RowInMappedWAEventNoId(dict):
    def get_item(self, key, default=""):
        return self.get(key, default)

    @classmethod
    def from_external_dict(cls, some_dict: dict):
        some_dict = clean_up_dict_with_nans(some_dict)
        return cls(some_dict)

    def as_dict(self) -> dict:
        row_as_dict = dict(self)

        return row_as_dict


    @property
    def registration_date(self):
        return self[REGISTRATION_DATE]


class MappedWAEventNoIDs(list):
    def __init__(self, list_of_rows: List[RowInMappedWAEventNoId]):
        super().__init__(list_of_rows)

    def __repr__(self):
        return str(self.to_df())

    def get_row_with_timestamp(self, timestamp):
        list_of_timestamps = self.list_of_timestamps()
        try:
            idx_of_timestamp = list_of_timestamps.index(timestamp)
        except ValueError:
            raise Exception("Timestamp %s not found in data" % str(timestamp))

        return self[idx_of_timestamp]

    def list_of_timestamps(self) -> list:
        return extract_list_of_entry_timestamps_from_existing_wa_event(self)

    def subset_with_timestamps(self, list_of_timestamps: list) -> "MappedWAEventNoIDs":
        subset = [row for row in self if row.registration_date in list_of_timestamps]
        return MappedWAEventNoIDs(subset)

    @classmethod
    def from_df(cls, some_df: pd.DataFrame):

        list_of_dicts = [
            RowInMappedWAEventNoId.from_external_dict(df_row.to_dict())
            for __, df_row in some_df.iterrows()
        ]
        return cls(list_of_dicts)

    @classmethod
    def from_dict(cls, some_dict: dict):
        df = pd.DataFrame(some_dict)
        transform_df_from_str_to_dates(df)
        return cls.from_df(df)

    def to_df(self) -> pd.DataFrame:
        list_of_dicts = [item.as_dict() for item in self]

        return pd.DataFrame(list_of_dicts)

    @classmethod
    def create_empty(cls):
        return cls([])


def extract_list_of_entry_timestamps_from_existing_wa_event(
    existing_mapped_wa_event_with_ids: MappedWAEventNoIDs,
) -> list:
    ## Entry timestamps are unique
    list_of_timestamps = [
        row_of_mapped_data.registration_date
        for row_of_mapped_data in existing_mapped_wa_event_with_ids
    ]

    return list_of_timestamps

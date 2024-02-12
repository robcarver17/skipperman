import datetime
from typing import List
import pandas as pd

from app.logic.events.import_wa.shared_state_tracking_and_data import MISSING_VALUE
from app.objects.utils import (
    clean_up_dict_with_nans,
    transform_df_from_str_to_dates,
transform_datetime_into_str
)

from app.objects.field_list import REGISTRATION_DATE, REGISTERED_BY_LAST_NAME, REGISTERED_BY_FIRST_NAME


def unique_row_identifier(registration_date: datetime.datetime, registered_by_last_name: str, registered_by_first_name: str) -> str:
    ## generate a unique hash from reg date, name, first name
    reg_datetime_as_str = transform_datetime_into_str(registration_date)
    row_id = "%s_%s_%s" % (reg_datetime_as_str, registered_by_last_name.lower().strip(), registered_by_first_name.lower().strip())

    return row_id


# can't use generic methods here as based on dataclasses
class RowInMappedWAEvent(dict):
    def __eq__(self, other: dict):
        my_keys = list(set(list(self.keys())))

        for key in my_keys:
            other_value = other.get(key, MISSING_VALUE)
            if other_value is MISSING_VALUE:
                return False
            my_value = self.get(key)

            if other_value==my_value:
                continue
            else:
                return False

        return True

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
    def row_id(self):
        return unique_row_identifier(registration_date=self.registration_date,
                                     registered_by_first_name=self.registered_by_first_name,
                                     registered_by_last_name=self.registered_by_last_name)

    @property
    def registration_date(self):
        return self[REGISTRATION_DATE]

    @property
    def registered_by_first_name(self):
        return self[REGISTERED_BY_FIRST_NAME]

    @property
    def registered_by_last_name(self):
        return self[REGISTERED_BY_LAST_NAME]


class MappedWAEvent(list):
    def __init__(self, list_of_rows: List[RowInMappedWAEvent]):
        super().__init__(list_of_rows)

    def __repr__(self):
        return str(self.to_df())

    def get_row_with_rowid(self, row_id):
        subset = self.subset_with_id(row_id)
        if len(subset)==0:
            raise Exception("Row ID %s not found in data" % str(row_id))
        if len(subset)>1:
            raise Exception("Duplicate row ID not allowed in data")

        return subset[0]

    def list_of_ids(self) -> list:
        return extract_list_of_row_ids_from_existing_wa_event(self)

    def subset_with_id(self, list_of_timestamps: list) -> "MappedWAEvent":
        subset = [row for row in self if row.row_id in list_of_timestamps]
        return MappedWAEvent(subset)

    @classmethod
    def from_df(cls, some_df: pd.DataFrame):

        list_of_dicts = [
            RowInMappedWAEvent.from_external_dict(df_row.to_dict())
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



def extract_list_of_row_ids_from_existing_wa_event(
    existing_mapped_wa_event_with_ids: MappedWAEvent,
) -> list:
    ## Entry timestamps are unique
    list_of_timestamps = [
        row_of_mapped_data.row_id
        for row_of_mapped_data in existing_mapped_wa_event_with_ids
    ]

    return list_of_timestamps

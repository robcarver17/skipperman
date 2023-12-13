from typing import List, Tuple
import pandas as pd

from app.objects.utils import (
    DictOfDictDiffs,
    create_dict_of_dict_diffs,
    clean_up_dict_with_nans,
    transform_df_from_dates_to_str,
transform_df_from_str_to_dates
)

from app.objects.field_list import REGISTRATION_DATE, WEEKEND_DAYS_ATTENDING_INPUT, DAYS_ATTENDING, ALL_DAYS_ATTENDING_INPUT
from app.objects.constants import arg_not_passed
from app.objects.day_selectors import weekend_day_selector_from_text, any_day_selector_from_text, DaySelector, ALL_DAYS_SELECTED, day_selector_stored_format_from_text, day_selector_to_text_in_stored_format


class RowInMappedWAEventNoId(dict):
    @classmethod
    def from_external_dict(cls, some_dict: dict):
        some_dict = clean_up_dict_with_nans(some_dict)
        some_dict = add_attendance_to_event_row(some_dict)
        return cls(some_dict)

    def as_dict(self) -> dict:
        row_as_dict = dict(self)
        translate_attendance_fields_to_text(row_as_dict)

        return row_as_dict

    def dict_of_row_diffs(
        self, other_dict: dict, comparing_fields=arg_not_passed
    ) -> DictOfDictDiffs:
        return create_dict_of_dict_diffs(
            self, other_dict, comparing_fields=comparing_fields
        )

    @property
    def registration_date(self):
        return self[REGISTRATION_DATE]

def add_attendance_to_event_row(row_as_dict: dict) -> dict:
    days_attending = get_attendance_selection_from_event_row(row_as_dict)
    row_as_dict[DAYS_ATTENDING] = days_attending

    return row_as_dict

def get_attendance_selection_from_event_row(
        row_as_dict: dict) -> DaySelector:

    if DAYS_ATTENDING in row_as_dict.keys():
        ## we've already processed days attending, so it will be stored in our internal format
        days_attending = day_selector_stored_format_from_text(row_as_dict[DAYS_ATTENDING])

    elif WEEKEND_DAYS_ATTENDING_INPUT in row_as_dict.keys():
        days_attending = weekend_day_selector_from_text(row_as_dict[WEEKEND_DAYS_ATTENDING_INPUT])

    elif ALL_DAYS_ATTENDING_INPUT in row_as_dict.keys():
        days_attending = any_day_selector_from_text(row_as_dict[WEEKEND_DAYS_ATTENDING_INPUT])

    else:
        days_attending = ALL_DAYS_SELECTED

    return days_attending

def remove_input_fields_from_wa_event_row(row_as_dict: dict):
    for key in [WEEKEND_DAYS_ATTENDING_INPUT, ALL_DAYS_ATTENDING_INPUT]:
        row_as_dict.pop(key)

def translate_attendance_fields_to_text(row_as_dict: dict):
    row_as_dict[DAYS_ATTENDING] = day_selector_to_text_in_stored_format(row_as_dict[DAYS_ATTENDING])


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

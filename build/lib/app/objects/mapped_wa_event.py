import datetime
from typing import List
import pandas as pd
from enum import Enum

from app.objects.utils import (
    clean_up_dict_with_nans,
    transform_df_from_str_to_dates,
transform_datetime_into_str
)

from app.data_access.configuration.field_list import REGISTRATION_DATE, REGISTERED_BY_LAST_NAME, REGISTERED_BY_FIRST_NAME

from app.data_access.configuration.configuration import WA_ACTIVE_STATUS, WA_CANCELLED_STATUS
from app.objects.constants import missing_data
from app.data_access.configuration.field_list import PAYMENT_STATUS

RegistrationStatus = Enum("RowStatus", ["Cancelled", "Active", "Deleted", "Empty", "Manual"])
cancelled_status = RegistrationStatus.Cancelled
active_status = RegistrationStatus.Active
deleted_status = RegistrationStatus.Deleted
empty_status = RegistrationStatus.Empty
manual_add_status = RegistrationStatus.Manual
all_possible_status = [cancelled_status, active_status, deleted_status, manual_add_status, empty_status]
all_possible_status_names = [status.name for status in all_possible_status]

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
            other_value = other.get(key,  missing_data)
            if other_value is missing_data:
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
    def registration_status(self) -> RegistrationStatus:
        return get_status_from_row_of_mapped_wa_event_data(self)

    @registration_status.setter
    def registration_status(self, new_status: RegistrationStatus):
        set_status_str_in_row_of_mapped_wa_event_data(self, new_status)

    @property
    def registration_date(self):
        return self[REGISTRATION_DATE]

    @registration_date.setter
    def registration_date(self, new_date: datetime.datetime):
        self[REGISTRATION_DATE] = new_date

    @property
    def registered_by_first_name(self):
        return self[REGISTERED_BY_FIRST_NAME]

    @property
    def registered_by_last_name(self):
        return self[REGISTERED_BY_LAST_NAME]



def get_status_from_row_of_mapped_wa_event_data(
    row_of_mapped_wa_event_data: RowInMappedWAEvent,
) -> RegistrationStatus:
    status_str = get_status_str_from_row_of_mapped_wa_event_data(
        row_of_mapped_wa_event_data
    )
    if status_str in all_possible_status_names:
        return RegistrationStatus[status_str]

    if status_str in WA_ACTIVE_STATUS:
        return active_status

    if status_str in WA_CANCELLED_STATUS:
        return cancelled_status

    if status_str=="":
        return empty_status

    raise Exception(
        "WA has used a status of %s in the mapped field %s, not recognised, update configuration.py"
        % (status_str, PAYMENT_STATUS)
    )



def set_status_str_in_row_of_mapped_wa_event_data(
    row_of_mapped_wa_event_data: RowInMappedWAEvent,
        new_status: RegistrationStatus
):
    row_of_mapped_wa_event_data[PAYMENT_STATUS] = new_status.name

def get_status_str_from_row_of_mapped_wa_event_data(
    row_of_mapped_wa_event_data: RowInMappedWAEvent,
) -> str:

    status_field = row_of_mapped_wa_event_data.get_item(
        PAYMENT_STATUS, missing_data
    )
    if status_field is missing_data:
        raise Exception(
            "Can't get status of entry because field %s is missing from mapping; check your field mapping"
            % PAYMENT_STATUS
        )

    return status_field




class MappedWAEvent(list):
    def __init__(self, list_of_rows: List[RowInMappedWAEvent]):
        super().__init__(list_of_rows)

    def __repr__(self):
        return str(self.to_df())

    def pop_id(self, row_id):
        idx = self.idx_with_id(row_id)
        self.pop(idx)

    def get_row_with_rowid(self, row_id):
        subset = self.subset_with_id(row_id)
        if len(subset)==0:
            raise Exception("Row ID %s not found in data" % str(row_id))
        if len(subset)>1:
            raise Exception("Duplicate row ID not allowed in data")

        return subset[0]

    def list_of_row_ids(self) -> list:
        return extract_list_of_row_ids_from_existing_wa_event(self)

    def remove_empty_status(self) -> "MappedWAEvent":
        return self.remove_status(empty_status)

    def remove_status(self, status_to_remove: RegistrationStatus) -> "MappedWAEvent":
        subset= [row for row in self if not row.registration_status == status_to_remove]
        return MappedWAEvent(subset)


    def active_registrations_only(self) -> "MappedWAEvent":
        return self.subset_on_status(active_status)

    def subset_on_status(self, status: RegistrationStatus) -> "MappedWAEvent":
        subset= [row for row in self if row.registration_status == status]
        return MappedWAEvent(subset)

    def idx_with_id(self, list_of_row_ids: list) -> int:
        subset = [row for row in self if row.row_id in list_of_row_ids]
        if len(subset)==0:
            return missing_data
        elif len(subset)>0:
            raise Exception("Duplicate row IDs")
        item = subset[0]

        return self.index(item)


    def subset_with_id(self, list_of_row_ids: list) -> "MappedWAEvent":
        subset = [row for row in self if row.row_id in list_of_row_ids]
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




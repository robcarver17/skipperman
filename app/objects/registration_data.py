import datetime
from copy import copy
from random import random
from typing import List
import pandas as pd

from app.data_access.configuration.configuration import UNABLE_TO_VOLUNTEER_KEYWORD_LIST
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjects,
    create_list_of_objects_from_dataframe,
    create_data_frame_given_list_of_objects,
)
from app.objects.utilities.generic_objects import GenericSkipperManObject
from app.objects.registration_status import (
    RegistrationStatus,
    empty_status,
    manual_status,
)
from app.objects.utilities.utils import (
    clean_up_dict_with_nans,
    transform_df_from_str_to_dates,
    transform_df_from_dates_to_str,
)

from app.data_access.configuration.field_list import (
    VOLUNTEER_STATUS,
    _ROW_ID,
    _REGISTRATION_STATUS,
    _SPECIAL_FIELDS,
    REGISTRATION_DATE,
    CADET_DATE_OF_BIRTH,
)
from app.objects.utilities.exceptions import missing_data, arg_not_passed
from app.objects.cadets import default_cadet


# can't use generic methods here as based on dataclasses
class RowInRegistrationData(GenericSkipperManObject, dict):
    def __eq__(self, other: dict):
        my_keys = self.list_of_keys_excluding_special_keys()

        for key in my_keys:
            other_value = other.get(key, missing_data)
            if other_value is missing_data:
                return False
            my_value = self.get(key)

            if other_value == my_value:
                continue
            else:
                return False

        return True

    def clear_values(self):
        my_keys = self.list_of_keys_excluding_special_keys()
        for key in my_keys:
            if key == REGISTRATION_DATE:
                pass

            elif key == CADET_DATE_OF_BIRTH:
                self[key] = default_cadet.date_of_birth

            else:
                self[key] = ""

    def get_item(self, key, default=""):
        return self.get(key, default)

    @classmethod
    def from_dict_of_str(cls, some_dict):
        some_dict = clean_up_dict_with_nans(some_dict)
        try:
            registration_status_as_str = some_dict.pop(_REGISTRATION_STATUS)
            registration_status = RegistrationStatus(registration_status_as_str)
        except:
            registration_status = empty_status

        some_dict[_REGISTRATION_STATUS] = registration_status

        return RowInRegistrationData(some_dict)

    def as_str_dict(self) -> dict:
        new_dict = dict(copy(self))
        new_dict[_REGISTRATION_STATUS] = new_dict[_REGISTRATION_STATUS].name

        return new_dict

    @classmethod
    def create_empty_with_manual_status_set(
        cls,
        fields: List[str],
        row_id: str,
        registration_datetime: datetime.datetime,
        date_of_birth: datetime.date,
    ):
        as_a_dict = dict([(key, "") for key in fields])

        for key in as_a_dict.keys():
            if key == REGISTRATION_DATE:
                as_a_dict[key] = registration_datetime

            if key == CADET_DATE_OF_BIRTH:
                as_a_dict[key] = date_of_birth

        as_a_dict[_ROW_ID] = str(row_id)
        as_a_dict[_REGISTRATION_STATUS] = manual_status

        return RowInRegistrationData(as_a_dict)

    def as_dict(self) -> dict:
        row_as_dict = dict(self)

        return row_as_dict

    def as_dict_excluding_special_keys(self) -> dict:
        row_as_dict = dict([(key, self[key]) for key in self.list_of_keys_excluding_special_keys()])

        return row_as_dict

    def list_of_keys_excluding_special_keys(self) -> List[str]:
        list_of_keys = copy(list(self.keys()))
        for special_key in _SPECIAL_FIELDS:
            list_of_keys.remove(special_key)

        return list_of_keys

    @property
    def row_id(self) -> str:
        return self.get(_ROW_ID, "")

    @row_id.setter
    def row_id(self, row_id: str):
        self[_ROW_ID] = row_id

    def replace_row_id_by_adding_random_number(self):
        existing_row_id = self.row_id
        self.row_id = replace_row_id_by_adding_random_number(existing_row_id)

    @property
    def registration_status(self) -> RegistrationStatus:
        reg_status = self.get(_REGISTRATION_STATUS, empty_status)

        return reg_status

    @registration_status.setter
    def registration_status(self, new_status: RegistrationStatus):
        self[_REGISTRATION_STATUS] = new_status


from app.objects.utilities.generic_list_of_objects import (
    get_unique_object_with_attr_in_list,
)


class RegistrationDataForEvent(GenericListOfObjects):
    def __init__(self, list_of_rows: List[RowInRegistrationData]):
        super().__init__(list_of_rows)

    @property
    def _object_class_contained(self):
        return RowInRegistrationData

    def __repr__(self):
        return str(self.to_df())

    def clear_user_data(self):
        for row in self:
            row.clear_values()

    def get_row_with_rowid(self, row_id: str, default=arg_not_passed):
        return get_unique_object_with_attr_in_list(
            some_list=self, attr_name="row_id", attr_value=row_id, default=default
        )

    def list_of_row_ids(self) -> list:
        return [reg_row.row_id for reg_row in self]

    def remove_empty_status(self) -> "RegistrationDataForEvent":
        return self.remove_rows_with_status(empty_status)

    def remove_rows_with_status(
        self, status_to_remove: RegistrationStatus
    ) -> "RegistrationDataForEvent":
        subset = [
            row for row in self if not row.registration_status == status_to_remove
        ]
        return RegistrationDataForEvent(subset)

    def active_registrations_only(self) -> "RegistrationDataForEvent":
        subset = [row for row in self if row.registration_status.is_active]
        return RegistrationDataForEvent(subset)

    def subset_with_list_of_row_ids(
        self, list_of_row_ids: list
    ) -> "RegistrationDataForEvent":
        subset = [row for row in self if row.row_id in list_of_row_ids]
        return RegistrationDataForEvent(subset)

    @classmethod
    def from_df_of_str(cls, df: pd.DataFrame):
        ## special methods as registration data contains date fields
        transform_df_from_str_to_dates(df)

        list_of_items = create_list_of_objects_from_dataframe(RowInRegistrationData, df)

        return cls(list_of_items)

    def as_df_of_str(self) -> pd.DataFrame:
        ## special methods as registration data contains date fields
        df = create_data_frame_given_list_of_objects(self)

        transform_df_from_dates_to_str(df)

        return df

    def list_of_fields(self) -> List[str]:
        df = self.as_df_of_str()

        return list(df.columns)

    def new_unique_row_id(self) -> str:
        list_of_row_ids = self.list_of_row_ids()

        return get_new_row_id_not_in_existing_list(list_of_row_ids)

    @classmethod
    def from_df(cls, some_df: pd.DataFrame):
        list_of_dicts = [
            RowInRegistrationData.from_dict_of_str(df_row.to_dict())
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


def summarise_status(mapped_event: RegistrationDataForEvent) -> dict:
    all_status = {}
    for row in mapped_event:
        status = row.registration_status
        current_count = all_status.get(status.name, 0)
        current_count += 1
        all_status[status.name] = current_count

    return all_status


def get_volunteer_status_from_row(row: RowInRegistrationData):
    return row.get_item(VOLUNTEER_STATUS, "")


def replace_row_id_by_adding_random_number(existing_row_id):
    add_on = str(int(random() * 100))
    return existing_row_id + "_" + add_on


def get_new_row_id_not_in_existing_list(list_of_row_ids: List[str]):
    not_unique = True
    while not_unique:
        new_row_id = "Manual_registration_%s" % str(int(random() * 100000))
        if new_row_id in list_of_row_ids:
            continue
        else:
            return new_row_id


def check_any_status_is_unable_given_list_of_status(list_of_status: List[str]):
    any_status_is_unable = any(
        [status for status in list_of_status if status_is_unable(status)]
    )

    return any_status_is_unable


def status_is_unable(status: str):
    for keyword in UNABLE_TO_VOLUNTEER_KEYWORD_LIST:
        if keyword in status.lower():
            return True

    return False

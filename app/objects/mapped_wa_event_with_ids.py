import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List

import pandas as pd

from app.data_access.configuration.configuration import ACTIVE_STATUS, CANCELLED_STATUS
from app.objects.constants import missing_data
from app.objects.field_list import PAYMENT_STATUS
from app.objects.utils import transform_str_from_date, similar, list_duplicate_indices

from app.objects.mapped_wa_event_no_ids import (
    RowInMappedWAEventNoId,
    extract_list_of_entry_timestamps_from_existing_wa_event,
)
from app.objects.cadets import ListOfCadets

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

    @property
    def cancelled_or_deleted(self) -> bool:
        status = get_status_from_row_of_mapped_wa_event_data(self)
        return status in [cancelled_status, deleted_status]

RowStatus = Enum("RowStatus", ["Cancelled", "Active", "Deleted"])


def get_status_from_row_of_mapped_wa_event_data(
    row_of_mapped_wa_event_data: RowInMappedWAEventWithId,
) -> RowStatus:

    status_str = get_status_str_from_row_of_mapped_wa_event_data(
        row_of_mapped_wa_event_data
    )
    if status_str in ACTIVE_STATUS:
        return RowStatus.Active

    if status_str in CANCELLED_STATUS:
        return RowStatus.Cancelled

    raise Exception(
        "WA has used a status of %s in the mapped field %s, not recognised, update configuration.py"
        % (status_str, PAYMENT_STATUS)
    )


def get_status_str_from_row_of_mapped_wa_event_data(
    row_of_mapped_wa_event_data: RowInMappedWAEventWithId,
) -> str:

    status_field = row_of_mapped_wa_event_data.get_data_attribute_or_missing_data(
        PAYMENT_STATUS
    )
    if status_field is missing_data:
        raise Exception(
            "Can't get status of entry because field %s is missing from mapping; check your field mapping"
            % PAYMENT_STATUS
        )

    return status_field


STATUS_FIELD = "row_status"
cancelled_status = RowStatus.Cancelled
active_status = RowStatus.Active
deleted_status = RowStatus.Deleted

all_possible_status = [cancelled_status, active_status, deleted_status]

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

    def index_of_duplicate_cadet_ids_ignore_cancelled_and_deleted(self):
        list_of_cadet_ids = self.list_of_cadet_ids
        duplicate_id_list = list_duplicate_indices(list_of_cadet_ids)
        list_of_cancelled_or_deleted_id = self._index_of_rows_that_are_cancelled_or_deleted()

        return filter_duplicate_list_to_remove_cancelled_or_delete(
            duplicate_id_list=duplicate_id_list,
            list_of_cancelled_or_deleted_id=list_of_cancelled_or_deleted_id
        )

    def _index_of_rows_that_are_cancelled_or_deleted(self) -> list:
        return [idx for idx,row in enumerate(self) if row.cancelled_or_deleted]

    @property
    def list_of_cadet_ids(self) -> list:
        return [row.cadet_id for row in self]


    @classmethod
    def create_empty(cls):
        return cls([])



def filter_duplicate_list_to_remove_cancelled_or_delete(
            duplicate_id_list: list,
            list_of_cancelled_or_deleted_id: list
        ):

    new_list_of_duplicates = []
    while len(duplicate_id_list)>0:
        next_duplicate_group = duplicate_id_list.pop()
        next_duplicate_group_without_cancelled_or_deleted = [idx for idx in next_duplicate_group
                                                             if idx not in list_of_cancelled_or_deleted_id]

        if len(next_duplicate_group_without_cancelled_or_deleted)>1:
            ## if 0 or 1 then no duplicates left
            new_list_of_duplicates.append(next_duplicate_group_without_cancelled_or_deleted)

    return new_list_of_duplicates



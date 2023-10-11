from copy import copy
from dataclasses import dataclass
from enum import Enum
from typing import List

import pandas as pd

from data_access.configuration.configuration import ACTIVE_STATUS, CANCELLED_STATUS
from objects.constants import missing_data
from objects.field_list import PAYMENT_STATUS
from objects.mapped_wa_event_no_ids import RowInMappedWAEventNoId
from objects.mapped_wa_event_with_ids import (
    RowInMappedWAEventWithId,
    MappedWAEventWithIDs,
    CADET_ID,
)
from objects.utils import DictOfDictDiffs

RowStatus = Enum("RowStatus", ["Cancelled", "Active", "Deleted"])
STATUS_FIELD = "row_status"
cancelled_status = RowStatus.Cancelled
active_status = RowStatus.Active
deleted_status = RowStatus.Deleted


@dataclass
class RowInMappedWAEventWithIdAndStatus:
    cadet_id: str
    data_in_row: RowInMappedWAEventNoId
    status: RowStatus

    def update_data_in_row(self, key, new_value):
        self.data_in_row[key] = new_value

    @classmethod
    def from_row_in_mapped_wa_event_with_id(
        cls, row_in_mapped_wa_event_with_id: RowInMappedWAEventWithId, status: RowStatus
    ):

        return cls(
            data_in_row=row_in_mapped_wa_event_with_id.data_in_row,
            cadet_id=row_in_mapped_wa_event_with_id.cadet_id,
            status=status,
        )

    def as_dict(self):
        data_in_row_as_dict = dict(self.data_in_row)
        data_in_row_as_dict.update(
            {CADET_ID: self.cadet_id, STATUS_FIELD: self.status.name}
        )
        return data_in_row_as_dict

    @classmethod
    def from_dict(cls, some_dict: dict):
        cadet_id = some_dict.pop(CADET_ID)
        status_str = some_dict.pop(STATUS_FIELD)
        status = RowStatus[status_str]

        return cls(
            cadet_id=cadet_id,
            status=status,
            data_in_row=RowInMappedWAEventNoId.from_external_dict(some_dict),
        )

    def dict_of_row_diffs_in_rowdata(
        self, other_row: "RowInMappedWAEventWithIdAndStatus"
    ) -> DictOfDictDiffs:
        return self.data_in_row.dict_of_row_diffs(other_row.data_in_row)


class MappedWAEventWithoutDuplicatesAndWithStatus(MappedWAEventWithIDs):
    def __init__(self, list_of_rows: List[RowInMappedWAEventWithIdAndStatus]):
        super().__init__(list_of_rows)

    def __repr__(self):
        return str(self.to_df())

    @classmethod
    def from_df(cls, some_df: pd.DataFrame):
        list_of_dicts = [
            RowInMappedWAEventWithIdAndStatus.from_dict(df_row.to_dict())
            for __, df_row in some_df.iterrows()
        ]
        return cls(list_of_dicts)

    def add_row(
        self,
        row_of_mapped_wa_event_data_with_status: RowInMappedWAEventWithIdAndStatus,
    ):
        cadet_id = row_of_mapped_wa_event_data_with_status.cadet_id

        try:
            assert not self.is_cadet_id_in_event(cadet_id)
        except:
            raise Exception(
                "Can't add a duplicate cadet ID to a WA event without duplication"
            )

        self.append(row_of_mapped_wa_event_data_with_status)

    def update_row(
        self,
        row_of_mapped_wa_event_data_with_id_and_status: RowInMappedWAEventWithIdAndStatus,
    ):
        cadet_id = row_of_mapped_wa_event_data_with_id_and_status.cadet_id
        list_of_cadet_ids = self.list_of_cadet_ids
        try:
            idx = list_of_cadet_ids.index(cadet_id)
        except ValueError:
            raise Exception("Can't update row as cadet id %s is missing" % cadet_id)

        # in place replacement
        self[idx] = row_of_mapped_wa_event_data_with_id_and_status

    def list_of_cadet_ids_with_given_status(self,  exclude_cancelled: bool = True,
                                 exclude_active: bool = False,
                                 exclude_deleted: bool =True) -> list:

        event_subsetted_for_given_status = self.subset_with_given_status(
            exclude_cancelled=exclude_cancelled,
            exclude_deleted=exclude_deleted,
            exclude_active=exclude_active
        )

        return event_subsetted_for_given_status.list_of_cadet_ids

    def subset_with_given_status(self, exclude_cancelled: bool = True,
                                 exclude_active: bool = False,
                                 exclude_deleted: bool =True) -> 'MappedWAEventWithoutDuplicatesAndWithStatus':

        new_subset = copy(self)
        if exclude_active:
            new_subset = [row for row in self if row.status is not active_status]
        if exclude_deleted:
            new_subset = [row for row in self if row.status is not deleted_status]
        if exclude_cancelled:
            new_subset = [row for row in self if row.status is not cancelled_status]

        return MappedWAEventWithoutDuplicatesAndWithStatus(new_subset)

    def cadet_ids_missing_from_new_list(self, list_of_cadet_ids: list):
        current_ids = self.list_of_cadet_ids

        return list(set(current_ids).difference(set(list_of_cadet_ids)))

    def is_cadet_status_deleted(self, cadet_id: str):
        row = self.get_row_with_id(cadet_id)
        return row.status is deleted_status

    def mark_cadet_as_cancelled(self, cadet_id: str):
        self.change_status_of_row(cadet_id=cadet_id, new_status=RowStatus.Cancelled)

    def mark_cadet_as_active(self, cadet_id: str):
        self.change_status_of_row(cadet_id=cadet_id, new_status=RowStatus.Active)

    def mark_cadet_as_deleted(self, cadet_id: str):
        self.change_status_of_row(cadet_id=cadet_id, new_status=RowStatus.Deleted)

    def change_status_of_row(self, cadet_id: str, new_status: RowStatus):
        relevant_row = self.get_row_with_id(cadet_id)
        relevant_row.status = new_status


def get_row_of_mapped_wa_event_data_with_status(
    row_in_mapped_wa_event_with_id: RowInMappedWAEventWithId,
):
    status = get_status_from_row_of_mapped_wa_event_data(row_in_mapped_wa_event_with_id)
    row_of_mapped_wa_event_data_with_status = (
        RowInMappedWAEventWithIdAndStatus.from_row_in_mapped_wa_event_with_id(
            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id, status=status
        )
    )

    return row_of_mapped_wa_event_data_with_status


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

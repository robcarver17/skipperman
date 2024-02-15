from copy import copy
from dataclasses import dataclass
from enum import Enum
from typing import List

import pandas as pd

from app.objects.mapped_wa_event import RowInMappedWAEvent, MappedWAEvent
from app.objects.mapped_wa_event_deltas import (
    RowInMappedWAEventDeltaRow,

)
from app.objects.day_selectors import DaySelector, day_selector_stored_format_from_text, day_selector_to_text_in_stored_format
from app.objects.food import FoodRequirements

CADET_ID = "cadet_id" ## must match
STATUS_FIELD = "status"
ATTENDANCE = "attendance"
FOOD_REQUIREMENTS = "food_requirements"

RowStatus = Enum("RowStatus", ["Cancelled", "Active", "Deleted"])

cancelled_status = RowStatus.Cancelled
active_status = RowStatus.Active
deleted_status = RowStatus.Deleted
all_possible_status = [cancelled_status, active_status, deleted_status]

@dataclass
class RowInMasterEvent:
    cadet_id: str
    data_in_row: RowInMappedWAEvent
    attendance: DaySelector
    status: RowStatus
    food_requirements: FoodRequirements

    def get_item(self, key, default=""):
        return self.data_in_row.get_item(key, default=default)

    def update_data_in_row(self, key, new_value):
        self.data_in_row[key] = new_value

    @classmethod
    def from_row_in_mapped_wa_event_with_id(
        cls, row_in_mapped_wa_event_with_id: RowInMappedWAEventDeltaRow, status: RowStatus,
            attendance: DaySelector,
            food_requirements: FoodRequirements
    ):
        return cls(
            data_in_row=row_in_mapped_wa_event_with_id.data_in_row,
            cadet_id=row_in_mapped_wa_event_with_id.cadet_id,
            status=status,
            attendance=attendance,
            food_requirements=food_requirements
        )

    def as_dict(self):
        data_in_row_as_dict = self.data_in_row.as_dict()
        data_in_row_as_dict.update(
            {CADET_ID: self.cadet_id, STATUS_FIELD: self.status.name,
             ATTENDANCE: day_selector_to_text_in_stored_format(self.attendance),
             FOOD_REQUIREMENTS: self.food_requirements.to_str()
             }
        )
        return data_in_row_as_dict

    @classmethod
    def from_dict(cls, some_dict: dict):
        cadet_id = str(some_dict.pop(CADET_ID))
        status = RowStatus[some_dict.pop(STATUS_FIELD)]
        attendance = day_selector_stored_format_from_text(some_dict.pop(ATTENDANCE))
        food_requirements = FoodRequirements.from_str(some_dict.pop(FOOD_REQUIREMENTS))

        return cls(
            cadet_id=cadet_id,
            status=status,
            data_in_row=RowInMappedWAEvent.from_external_dict(some_dict),
            attendance=attendance,
            food_requirements=food_requirements
        )


    def mark_as_deleted(self):
        self.status = deleted_status

    def is_deleted(self):
        return self.status == deleted_status


class MasterEvent(MappedWAEvent):
    def __init__(self, list_of_rows: List[RowInMasterEvent]):
        super().__init__(list_of_rows)

    def __repr__(self):
        return str(self.to_df())

    @classmethod
    def from_df(cls, some_df: pd.DataFrame):
        list_of_dicts = [
            RowInMasterEvent.from_dict(df_row.to_dict())
            for __, df_row in some_df.iterrows()
        ]
        return cls(list_of_dicts)

    def add_row(
        self,
        row_of_mapped_wa_event_data_with_status: RowInMasterEvent,
    ):
        cadet_id = row_of_mapped_wa_event_data_with_status.cadet_id

        try:
            assert not self.is_cadet_id_in_event(cadet_id)
        except:
            raise Exception("Can't add a duplicate cadet ID to master event data")

        self.append(row_of_mapped_wa_event_data_with_status)

    def update_row(
        self,
        row_of_mapped_wa_event_data_with_id_and_status: RowInMasterEvent,
    ):
        cadet_id = row_of_mapped_wa_event_data_with_id_and_status.cadet_id
        list_of_cadet_ids = self.list_of_cadet_ids
        try:
            idx = list_of_cadet_ids.index(cadet_id)
        except ValueError:
            raise Exception("Can't update row as cadet id %s is missing" % cadet_id)

        # in place replacement
        self[idx] = row_of_mapped_wa_event_data_with_id_and_status

    def list_of_active_cadet_ids(
        self,
    ) -> list:
        return self.list_of_cadet_ids_with_given_status(
            exclude_cancelled= True,
            exclude_active= False,
        exclude_deleted = True,
        )

    def list_of_cadet_ids_with_given_status(
        self,
        exclude_cancelled: bool = True,
        exclude_active: bool = False,
        exclude_deleted: bool = True,
    ) -> list:
        event_subsetted_for_given_status = self.subset_with_given_status(
            exclude_cancelled=exclude_cancelled,
            exclude_deleted=exclude_deleted,
            exclude_active=exclude_active,
        )

        return event_subsetted_for_given_status.list_of_cadet_ids

    def subset_with_given_status(
        self,
        exclude_cancelled: bool = True,
        exclude_active: bool = False,
        exclude_deleted: bool = True,
    ) -> "MasterEvent":
        new_subset = copy(self)
        if exclude_active:
            new_subset = [row for row in new_subset if row.status is not active_status]
        if exclude_deleted:
            new_subset = [row for row in new_subset  if row.status is not deleted_status]
        if exclude_cancelled:
            new_subset = [row for row in new_subset if row.status is not cancelled_status]

        return MasterEvent(new_subset)

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

    def sort_given_superset_of_cadet_ids(self, list_of_ids):
        new_master_event_list = [self.get_row_with_id(cadet_id) for cadet_id in list_of_ids if self.is_cadet_id_in_event(cadet_id)]
        return MasterEvent(new_master_event_list)

def get_row_of_master_event_from_mapped_row_with_idx_and_status(*args, **kwargs):
    pass
"""
def get_row_of_master_event_from_mapped_row_with_idx_and_status(
    row_in_mapped_wa_event_with_id: RowInMappedWAEventDeltaRow,
        event: Event
) -> RowInMasterEvent:

    status = get_status_from_row_of_mapped_wa_event_data(row_in_mapped_wa_event_with_id)
    attendance = get_attendance_selection_from_event_row(row_in_mapped_wa_event_with_id, event=event)
    food_requirements = get_cadet_food_requirements_from_row_of_mapped_wa_event_data(row_in_mapped_wa_event_with_id)

    row_of_mapped_wa_event_data_with_status = (
        RowInMasterEvent.from_row_in_mapped_wa_event_with_id(
            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id, status=status,
            attendance=attendance,
            food_requirements=food_requirements
            )
    )

    return row_of_mapped_wa_event_data_with_status



def get_attendance_selection_from_event_row(
        row: RowInMappedWAEvent, event: Event) -> DaySelector:

    row_as_dict = row.as_dict()

    if WEEKEND_DAYS_ATTENDING_INPUT in row_as_dict.keys():
        return weekend_day_selector_from_text(row_as_dict[WEEKEND_DAYS_ATTENDING_INPUT])

    elif ALL_DAYS_ATTENDING_INPUT in row_as_dict.keys():
        return any_day_selector_from_short_form_text(row_as_dict[WEEKEND_DAYS_ATTENDING_INPUT])

    return event.day_selector_with_covered_days()




def get_status_from_row_of_mapped_wa_event_data(
    row_of_mapped_wa_event_data: RowInMappedWAEvent,
) -> RowStatus:
    status_str = get_status_str_from_row_of_mapped_wa_event_data(
        row_of_mapped_wa_event_data
    )
    if status_str in ACTIVE_STATUS:
        return active_status

    if status_str in CANCELLED_STATUS:
        return cancelled_status

    raise Exception(
        "WA has used a status of %s in the mapped field %s, not recognised, update configuration.py"
        % (status_str, PAYMENT_STATUS)
    )


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



"""

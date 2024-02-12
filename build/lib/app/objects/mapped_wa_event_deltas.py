from dataclasses import dataclass
from typing import List

import pandas as pd

from app.objects.food import FoodRequirements, guess_food_requirements_from_food_field
from app.objects.utils import clean_up_dict_with_nans
from app.objects.constants import missing_data
from app.objects.field_list import CADET_FOOD_PREFERENCE

from app.objects.mapped_wa_event import (
    RowInMappedWAEvent,
    extract_list_of_row_ids_from_existing_wa_event,
MappedWAEvent
)
from app.objects.constants import NoCadets, DuplicateCadets

CHANGED_ROW = "changed_row"
DELETED_ROW = "deleted_row"
UNCHANGED_ROW = "unchanged_row"
NEW_ROW = "new_row"

ROW_ID = "cadet_id" ## must match
ROW_STATUS = "row_status"
@dataclass
class RowInMappedWAEventDeltaRow:
    row_id: str
    data_in_row: RowInMappedWAEvent
    row_status: str

    def get_data_attribute_or_missing_data(self, attr_name: str):
        return self.data_in_row.get(attr_name, missing_data)

    def as_dict(self):
        data_in_row_as_dict = self.data_in_row.as_dict()
        data_in_row_as_dict.update({ROW_ID: self.row_id})
        data_in_row_as_dict.update({ROW_STATUS: self.row_status})

        return data_in_row_as_dict

    @property
    def is_deleted_row(self):
        return self.row_status==DELETED_ROW

    @property
    def is_changed_row(self):
        return self.row_status==CHANGED_ROW

    @property
    def is_new_row(self):
        return self.row_status==NEW_ROW

    @property
    def is_unchanged_row(self):
        return self.row_status==UNCHANGED_ROW

    @classmethod
    def unchanged_row(cls, row_id: str, data_in_row: RowInMappedWAEvent):
        return cls(row_id=row_id, row_status=UNCHANGED_ROW, data_in_row=data_in_row)

    @classmethod
    def changed_row(cls, row_id: str, data_in_row: RowInMappedWAEvent):
        return cls(row_id=row_id, row_status=CHANGED_ROW, data_in_row=data_in_row)

    @classmethod
    def new_row(cls, row_id: str, data_in_row: RowInMappedWAEvent):
        return cls(row_id=row_id, row_status=NEW_ROW, data_in_row=data_in_row)

    @classmethod
    def deleted_row(cls, row_id: str, data_in_row: RowInMappedWAEvent):
        return cls(row_id=row_id, row_status=DELETED_ROW, data_in_row=data_in_row)

    @classmethod
    def from_dict(cls, some_dict: dict):
        some_dict = clean_up_dict_with_nans(some_dict)
        row_id = str(some_dict.pop(ROW_ID))
        row_status = str(some_dict.pop(ROW_STATUS))

        return cls(
            row_id=row_id,
            row_status=row_status,
            data_in_row=RowInMappedWAEvent.from_external_dict(some_dict),
        )


class MappedWAEventListOfDeltaRows(list):
    def __init__(self, list_of_rows: List[RowInMappedWAEventDeltaRow]):
        super().__init__(list_of_rows)

    def __repr__(self):
        return str(self.to_df())

    @property
    def count_of_changed(self) -> int:
        return sum([row for row in self if row.is_changed_row])

    @property
    def count_of_new(self) -> int:
        return sum([row for row in self if row.is_changed_row])

    @property
    def count_of_deleted(self) -> int:
        return sum([row for row in self if row.is_deleted_row])

    @property
    def count_of_unchanged(self) -> int:
        return sum([row for row in self if row.is_unchanged_row])


    @classmethod
    def from_df(cls, some_df: pd.DataFrame):
        list_of_dicts = [
            RowInMappedWAEventDeltaRow.from_dict(df_row.to_dict())
            for __, df_row in some_df.iterrows()
        ]
        return cls(list_of_dicts)

    def to_df(self) -> pd.DataFrame:
        list_of_dicts = [item.as_dict() for item in self]

        return pd.DataFrame(list_of_dicts)


    @classmethod
    def create_empty(cls):
        return cls([])

from app.objects.utils import in_x_not_in_y, in_both_x_and_y

def create_list_of_delta_rows(original_event: MappedWAEvent,
                              new_event: MappedWAEvent) -> MappedWAEventListOfDeltaRows:

    list_of_ids_in_original = original_event.list_of_ids()
    list_of_ids_in_new = new_event.list_of_ids()

    deleted_row_ids = in_x_not_in_y(x=list_of_ids_in_original, y=list_of_ids_in_new)
    new_row_ids = in_x_not_in_y(x=list_of_ids_in_new, y=list_of_ids_in_original)
    existing_row_ids = in_both_x_and_y(list_of_ids_in_new, list_of_ids_in_original)

    deleted_rows = deleted_delta_rows(original_event=original_event, deleted_row_ids=deleted_row_ids)
    existing_rows = existing_delta_rows(new_event=new_event, original_event=original_event, existing_row_ids=existing_row_ids)
    new_rows = new_delta_rows(new_event=new_event, new_row_ids=new_row_ids)

    return MappedWAEventListOfDeltaRows(deleted_rows+new_rows+existing_rows)

def deleted_delta_rows(original_event: MappedWAEvent, deleted_row_ids:list) ->  MappedWAEventListOfDeltaRows:
    deleted_rows = [RowInMappedWAEventDeltaRow.deleted_row(
        row_id=row_id,
        data_in_row=original_event.get_row_with_rowid(row_id))
        for row_id in deleted_row_ids]

    return MappedWAEventListOfDeltaRows(deleted_rows)

def new_delta_rows(new_event: MappedWAEvent, new_row_ids: list) ->  MappedWAEventListOfDeltaRows:
    new_rows = [RowInMappedWAEventDeltaRow.new_row(
        row_id=row_id,
        data_in_row=new_event.get_row_with_rowid(row_id))
        for row_id in new_row_ids]

    return MappedWAEventListOfDeltaRows(new_rows)


def existing_delta_rows(original_event: MappedWAEvent, new_event:MappedWAEvent, existing_row_ids: list ) ->  MappedWAEventListOfDeltaRows:
    existing_rows = []
    for row_id in existing_row_ids:
        original_row = original_event.get_row_with_rowid(row_id)
        new_row = new_event.get_row_with_rowid(row_id)

        if original_row==new_row:
            existing_rows.append(RowInMappedWAEventDeltaRow.unchanged_row(row_id=row_id, data_in_row=original_row))
        else:
            existing_rows.append(RowInMappedWAEventDeltaRow.changed_row(row_id=row_id, data_in_row=new_row))

    return MappedWAEventListOfDeltaRows(existing_rows)


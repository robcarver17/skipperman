from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

import pandas as pd
from app.objects.cadets import Cadet

from app.objects.generic_list_of_objects import (
    GenericListOfObjects,
)
from app.objects.substages import TickSheetItem

Tick = Enum("Tick", ["Full", "Half", "NotApplicable", "NoTick"])

full_tick = Tick.Full
half_tick = Tick.Half
not_applicable_tick = Tick.NotApplicable
no_tick = Tick.NoTick

tick_strings_dict = {
    full_tick: "X",
    half_tick: "1/2",
    not_applicable_tick: "N A",
    no_tick: "[  ]",
}
string_ticks_dict = {v: k for k, v in tick_strings_dict.items()}


@dataclass
class TickWithItem:
    tick_item_id: str
    tick: Tick


def tick_as_str(tick: Tick) -> str:
    return tick_strings_dict[tick]


def tick_from_str(some_str: str) -> Tick:
    return string_ticks_dict[some_str]


class DictOfTicksWithItem(Dict[str, Tick]):
    def update_tick(self, new_tick: Tick, tick_item: TickSheetItem):
        ## have to modify underlying data so stored properly, don't actually have to modify this object as only intermediate
        self[tick_item.id] = new_tick

    def list_of_ticks(self) -> List[Tick]:
        return list(self.values())

    def add_all_ticks_inplace(self):
        for tick_item_id in self.keys():
            self[tick_item_id] = full_tick

    def as_dict_of_str_aligned_to_list_of_tick_list_items(
        self, list_of_tick_list_items: List[str]
    ):
        return dict(
            [
                (tick_item_id, tick_as_str(self.get(tick_item_id, no_tick)))
                for tick_item_id in list_of_tick_list_items
            ]
        )

    def get_tick_with_id(self, tick_item_id) -> Tick:
        return self.get(tick_item_id, no_tick)

    @classmethod
    def from_dict_of_str(cls, dict_of_str):
        as_dict_of_ticks_with_items = dict(
            [
                (tick_item_id, tick_from_str(tick_str))
                for tick_item_id, tick_str in dict_of_str.items()
            ]
        )

        return cls(as_dict_of_ticks_with_items)


CADET_ID = "cadet_id"


@dataclass
class CadetIdWithTickListItemIds:
    cadet_id: str
    dict_of_ticks_with_items: DictOfTicksWithItem

    def update_tick(self, new_tick: Tick, tick_item: TickSheetItem):
        ## have to modify underlying data so stored properly, don't actually have to modify this object as only intermediate
        self.dict_of_ticks_with_items.update_tick(
            new_tick=new_tick, tick_item=tick_item
        )

    def add_all_ticks_inplace(self):
        self.dict_of_ticks_with_items.add_all_ticks_inplace()

    @property
    def list_of_tick_item_ids(self) -> List[str]:
        tick_list_items = list(self.dict_of_ticks_with_items.keys())
        return tick_list_items

    def as_dict_of_str_aligned_to_list_of_tick_list_items(
        self, list_of_tick_list_items: List[str]
    ):
        cadet_id_dict = {CADET_ID: self.cadet_id}
        dict_of_ticks_with_items_as_str = self.dict_of_ticks_with_items.as_dict_of_str_aligned_to_list_of_tick_list_items(
            list_of_tick_list_items
        )
        dict_of_ticks_with_items_as_str[CADET_ID] = self.cadet_id

        return {**cadet_id_dict, **dict_of_ticks_with_items_as_str}  ## merge dict

    @classmethod
    def from_dict_of_str(cls, dict_of_str: dict):
        cadet_id = dict_of_str.pop(CADET_ID)
        dict_of_ticks_with_items = DictOfTicksWithItem.from_dict_of_str(dict_of_str)

        return cls(cadet_id=cadet_id, dict_of_ticks_with_items=dict_of_ticks_with_items)


class ListOfCadetIdsWithTickListItemIds(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetIdWithTickListItemIds

    def to_df(self) -> pd.DataFrame:
        return self.as_df_of_str()

    def as_df_of_str(self) -> pd.DataFrame:
        return list_of_cadets_with_tick_list_items_as_df(self)

    def append(self, __object):
        raise Exception("Can't append use add or modify specific tick")

    @classmethod
    def from_df_of_str(cls, df: pd.DataFrame):
        list_of_cadets_with_tick_list_items = (
            from_df_to_list_of_cadets_with_tick_list_items(df)
        )

        return cls(list_of_cadets_with_tick_list_items)

    def update_tick(self, cadet: Cadet, new_tick: Tick, tick_item: TickSheetItem):
        ## have to modify underlying data so stored properly, don't actually have to modify this object as only intermediate
        tick_list_items_for_cadet = self[self.index_of_cadet_id(cadet_id=cadet.id)]
        tick_list_items_for_cadet.update_tick(new_tick=new_tick, tick_item=tick_item)

    def index_of_cadet_id(self, cadet_id: str):
        list_of_ids = self.list_of_cadet_ids

        return list_of_ids.index(cadet_id)

    @property
    def list_of_cadet_ids(self):
        return [str(item.cadet_id) for item in self]

    def list_of_tick_list_item_ids(self) -> List[str]:
        first_cadet = self[0]
        tick_list_items = first_cadet.list_of_tick_item_ids

        return tick_list_items


def list_of_cadets_with_tick_list_items_as_df(
    list_of_cadets_with_tick_list_items: ListOfCadetIdsWithTickListItemIds,
) -> pd.DataFrame:
    list_of_tick_list_items = (
        list_of_cadets_with_tick_list_items.list_of_tick_list_item_ids()
    )
    list_of_cadets_with_tick_list_items_as_dict_of_str = [
        cadet_with_tick_list_items.as_dict_of_str_aligned_to_list_of_tick_list_items(
            list_of_tick_list_items
        )
        for cadet_with_tick_list_items in list_of_cadets_with_tick_list_items
    ]

    return pd.DataFrame(list_of_cadets_with_tick_list_items_as_dict_of_str)


def from_df_to_list_of_cadets_with_tick_list_items(
    df: pd.DataFrame,
) -> ListOfCadetIdsWithTickListItemIds:
    list_of_cadets_with_tick_lists = []
    for i in range(len(df)):
        row = df.iloc[i]
        cadet_with_tick_list_items = CadetIdWithTickListItemIds.from_dict_of_str(
            row.to_dict()
        )
        list_of_cadets_with_tick_lists.append(cadet_with_tick_list_items)

    return ListOfCadetIdsWithTickListItemIds(list_of_cadets_with_tick_lists)


list_of_tick_options = [no_tick, half_tick, full_tick, not_applicable_tick]

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

import pandas as pd

from app.objects.utilities.generic_list_of_objects import GenericListOfObjects

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

list_of_tick_options = [no_tick, half_tick, full_tick, not_applicable_tick]


@dataclass
class TickWithItem:
    tick_item_id: str
    tick: Tick


def tick_as_str(tick: Tick) -> str:
    return tick_strings_dict[tick]


def tick_from_str(some_str: str) -> Tick:
    return string_ticks_dict[some_str]


class DictOfTicksWithItem(Dict[str, Tick]):

    def as_dict_of_str_aligned_to_list_of_tick_list_items(
        self, list_of_tick_list_items: List[str]
    ):
        return dict(
            [
                (tick_item_id, tick_as_str(self.get(tick_item_id, no_tick)))
                for tick_item_id in list_of_tick_list_items
            ]
        )


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

    @classmethod
    def create_empty(cls, cadet_id: str):
        return cls(cadet_id=cadet_id, dict_of_ticks_with_items=DictOfTicksWithItem())

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


NOTIONAL_CADET_ID_NOT_USED = "**notional***"


class ListOfTickListItemsAndTicksForSpecificCadet(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetIdWithTickListItemIds

    def to_df(self) -> pd.DataFrame:
        return self.as_df_of_str()

    def as_df_of_str(self) -> pd.DataFrame:
        return list_of_cadets_with_tick_list_items_as_df(self)

    @classmethod
    def from_df_of_str(cls, df: pd.DataFrame):
        list_of_cadets_with_tick_list_items = (
            from_df_to_list_of_cadets_with_tick_list_items(df)
        )

        return cls(list_of_cadets_with_tick_list_items)



    def list_of_tick_list_item_ids(self) -> List[str]:
        if len(self) == 0:
            return []
        first_cadet = self[0]
        tick_list_items = first_cadet.list_of_tick_item_ids

        return tick_list_items


def list_of_cadets_with_tick_list_items_as_df(
    list_of_cadets_with_tick_list_items: ListOfTickListItemsAndTicksForSpecificCadet,
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
) -> ListOfTickListItemsAndTicksForSpecificCadet:
    list_of_cadets_with_tick_lists = []
    for i in range(len(df)):
        row = df.iloc[i]
        cadet_with_tick_list_items = CadetIdWithTickListItemIds.from_dict_of_str(
            row.to_dict()
        )
        list_of_cadets_with_tick_lists.append(cadet_with_tick_list_items)

    return ListOfTickListItemsAndTicksForSpecificCadet(list_of_cadets_with_tick_lists) ## ignore warning

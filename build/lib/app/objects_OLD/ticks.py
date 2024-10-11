from copy import copy
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

import pandas as pd
from app.objects.qualifications import Qualification

from app.objects.day_selectors import ListOfDaySelectors

from app.objects.exceptions import missing_data, arg_not_passed
from app.objects.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    GenericListOfObjects,
)
from app.objects.generic_objects import GenericSkipperManObjectWithIds


@dataclass
class LabelledTickSheetWithCadetIds:
    df: pd.DataFrame
    list_of_cadet_ids: List[str]
    cadets_in_columns: bool = False
    qualification_name: str = ""
    group_name: str = ""

    def from_existing_replace_df(self, new_df: pd.DataFrame):
        return LabelledTickSheetWithCadetIds(
            df=new_df,
            list_of_cadet_ids=self.list_of_cadet_ids,
            cadets_in_columns=self.cadets_in_columns,
            qualification_name=self.qualification_name,
            group_name=self.group_name,
        )

    def transpose(self):
        now_cadets_in_columns = not self.cadets_in_columns
        new_version = copy(self)
        new_version.df = new_version.df.transpose()
        new_version.cadets_in_columns = now_cadets_in_columns

        return new_version

    def add_attendance_data(self, attendance_data: ListOfDaySelectors):
        attendance = attendance_data.as_pd_data_frame()
        dummy_multindex = [[""] * len(attendance.columns), attendance.columns]
        attendance.columns = dummy_multindex
        qual_multindex = pd.MultiIndex.from_tuples(
            [("%s:" % self.qualification_name.upper(), "")]
        )
        qual_row = pd.DataFrame("", index=qual_multindex, columns=self.df.columns)
        qual_column = pd.DataFrame("", index=self.df.index, columns=qual_multindex)

        if self.cadets_in_columns:
            attendance = attendance.transpose()
            attendance.columns = self.df.columns
            new_df = pd.concat([attendance, qual_row, self.df], axis=0)
        else:
            attendance.index = self.df.index
            new_df = pd.concat([attendance, qual_column, self.df], axis=1)

        return self.from_existing_replace_df(new_df)

    def add_health_notes(self, health_notes: List[str]):
        print(health_notes)
        health_multindex = pd.MultiIndex.from_tuples([("", "Medical notes")])
        if self.cadets_in_columns:
            health_row = pd.DataFrame(
                health_notes, index=health_multindex, columns=self.df.columns
            )
            print(health_row)
            new_df = pd.concat([self.df, health_row], axis=0)
        else:
            health_column = pd.DataFrame(
                health_notes, index=self.df.index, columns=health_multindex
            )
            print(health_column)
            new_df = pd.concat([self.df, health_column], axis=1)

        return self.from_existing_replace_df(new_df)

    def add_qualification_and_group_header(self):
        qual_multindex = pd.MultiIndex.from_tuples(
            [("%s:" % self.qualification_name.upper(), self.group_name)]
        )

        if self.cadets_in_columns:
            qual_row = pd.DataFrame("", index=qual_multindex, columns=self.df.columns)
            new_df = pd.concat([qual_row, self.df], axis=0)
        else:
            qual_column = pd.DataFrame("", index=self.df.index, columns=qual_multindex)
            new_df = pd.concat([qual_column, self.df], axis=1)

        return self.from_existing_replace_df(new_df)

    def add_club_boat_asterix(self, list_of_club_boat_bool: List[bool]):
        new_df = copy(self.df)
        list_of_club_boat_asterix = [
            "*" if yes else " " for yes in list_of_club_boat_bool
        ]
        if self.cadets_in_columns:
            new_df.columns = [
                column + star
                for column, star in zip(new_df.columns, list_of_club_boat_asterix)
            ]
        else:
            new_df.index = [
                column + star
                for column, star in zip(new_df.index, list_of_club_boat_asterix)
            ]

        return self.from_existing_replace_df(new_df)


@dataclass
class TickSubStage(GenericSkipperManObjectWithIds):
    name: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class ListOfTickSubStages(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return TickSubStage

    def name_given_id(self, id: str) -> str:
        names = [item.name for item in self if item.id == id]

        if len(names) == 0:
            return missing_data
        elif len(names) > 1:
            raise Exception(
                "Found more than one substage with same ID should be impossible"
            )

        return names[0]

    def idx_given_name(self, name: str):
        id = self.id_given_name(name)
        if id is missing_data:
            return missing_data
        return self.index_of_id(id)

    def id_given_name(self, name: str):
        id = [item.id for item in self if item.name == name]

        if len(id) == 0:
            return missing_data
        elif len(id) > 1:
            raise Exception(
                "Found more than one substage with same name should be impossible"
            )

        return str(id[0])

    def add(self, name: str):
        sub_stage = TickSubStage(name=name)
        try:
            assert name not in self.list_of_names()
        except:
            raise Exception("Can't add duplicate substage %s already exists" % name)
        sub_stage.id = self.next_id()

        self.append(sub_stage)


    def modify_name_of_substage_where_new_name_also_does_not_exist(self, substage_id: str, new_name: str):

        items = [item for item in self if item.id == substage_id]
        assert len(items)==1

        item = items[0]
        item.name = new_name


    def list_of_names(self):
        return [sub_stage.name for sub_stage in self]

PLACEHOLDER_TICK_SHEET_ID = str(-9999)

@dataclass
class TickSheetItem(GenericSkipperManObjectWithIds):
    name: str
    stage_id: str
    substage_id: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name

    @classmethod
    def create_placeholder(cls, stage_id: str, substage_id: str):
        return cls(name='', substage_id=substage_id, stage_id=stage_id, id=PLACEHOLDER_TICK_SHEET_ID)

    @property
    def is_placeholder(self):
        return self.id==PLACEHOLDER_TICK_SHEET_ID

class ListOfTickSheetItems(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return TickSheetItem

    def switch_all_instances_of_substage_for_qualification(self, existing_substage_id: str,
                             stage_id: str,
                             new_substage_id: str):

        for item in self:
            if item.substage_id==existing_substage_id and item.stage_id==stage_id:
                item.substage_id =new_substage_id

    def only_this_qualification_has_this_substage(self, substage_id: str,
                                                                                  stage_id:str)->bool:

        substage_exists_in_another_stage = [True for item in self if (not item.stage_id==stage_id) and (item.substage_id==substage_id)]

        return not any(substage_exists_in_another_stage)

    def modify_ticksheet_item_name(self, tick_item_id:str,
                                                            new_item_name:str):

        idx = self.index_of_id(tick_item_id)
        item = self[idx]
        item.name = new_item_name


    def add(self, name: str, stage_id: str, substage_id: str):
        ## Duplicates aren't a problem... are they?
        try:
            assert not self.name_and_id_already_exists(name=name, substage_id=substage_id, stage_id=stage_id)
        except:
            raise Exception("Can't create duplicate tick sheet item name '%s' for existing substage and stage" % name)

        id = self.next_id()
        self.append(TickSheetItem(name=name, stage_id=stage_id, substage_id=substage_id, id=id))
        self.delete_placeholder_if_only_entry(stage_id=stage_id, substage_id=substage_id)

    def name_and_id_already_exists(self,  name: str, stage_id: str, substage_id: str):
        list_of_items = [item for item in self if item.name==name and item.substage_id==substage_id and item.stage_id==stage_id]
        return len(list_of_items)>0

    def delete_placeholder_if_only_entry(self,  stage_id: str, substage_id: str):
        if self.placeholders_exist(stage_id=stage_id, substage_id=substage_id):
            self.delete_placeholder(stage_id=stage_id, substage_id=substage_id)

    def delete_placeholder(self,  stage_id: str, substage_id: str):
        list_of_items = [item for item in self if item.stage_id==stage_id and item.substage_id==substage_id and item.is_placeholder]
        assert len(list_of_items)==1
        self.remove(list_of_items[0])

    def add_placeholder(self, stage_id: str, substage_id: str):
        try:
            assert not self.placeholders_exist(stage_id=stage_id, substage_id=substage_id)
        except:
            raise Exception("Can't add more than once placeholder for a substage")

        self.append(TickSheetItem.create_placeholder(stage_id=stage_id, substage_id=substage_id))

    def placeholders_exist(self,  stage_id: str, substage_id: str):
        return any([True for item in self if item.stage_id==stage_id and item.substage_id==substage_id and item.is_placeholder])

    def subset_for_substage_id_ignoring_placeholders(self, substage_id: str):
        new_list = [item for item in self if item.substage_id == substage_id and not item.is_placeholder]

        return ListOfTickSheetItems(new_list)

    def subset_for_qualification_stage_id(self, stage_id: str, ignore_placeholders: bool = True) -> 'ListOfTickSheetItems':
        new_list = [item for item in self if item.stage_id == stage_id]
        if ignore_placeholders:
            new_list = [item for item in new_list if not item.is_placeholder]

        return ListOfTickSheetItems(new_list)

    def list_of_item_names(self) -> List[str]:
        return [item.name for item in self]

    def list_of_substage_ids(self) -> List[str]:
        return [item.substage_id for item in self]


class TickSubStagesAsDict(Dict[TickSubStage, ListOfTickSheetItems]):
    def substage_names(self):
        list_of_substages = list(self.keys())
        return [substage.name for substage in list_of_substages]


class QualificationsAndTickItemsAsDict(Dict[Qualification, TickSubStagesAsDict]):
    def list_of_substage_names(self):
        list_of_substage_names = []
        for tick_substages_dict in self.values():
            substage_names = tick_substages_dict.substage_names()
            list_of_substage_names+=substage_names

        return list(set(list_of_substage_names))


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


class DictOfTicksWithItem(dict):
    def percentage_complete(self) -> float:
        full_ticks = [1.0 for tick in self.list_of_ticks() if tick == full_tick]
        half_ticks = [0.5 for tick in self.list_of_ticks() if tick == half_tick]

        total_Ticks = float(len(self.list_of_ticks()))

        return (sum(full_ticks) + sum(half_ticks)) / total_Ticks

    def list_of_ticks(self) -> List[Tick]:
        return list(self.values())

    def list_of_item_ids(self) -> List[Tick]:
        return list(self.keys())

    def add_all_ticks_inplace(self):
        for tick_item_id in self.keys():
            self[tick_item_id] = full_tick

    def with_all_empty(self):
        new_dict = dict([(tick_item_id, no_tick) for tick_item_id in self.keys()])
        return DictOfTicksWithItem(new_dict)

    @classmethod
    def from_list_of_ticks_with_items(
        cls, list_of_ticks_with_items: List[TickWithItem]
    ):
        as_dict = dict(
            [
                (tick_with_item.tick_item_id, tick_with_item.tick)
                for tick_with_item in list_of_ticks_with_items
            ]
        )
        return cls(as_dict)

    def aligned_to_list_of_tick_list_items(self, list_of_tick_list_items: List[str]):
        as_dict = dict(
            [
                (tick_item_id, self.get(tick_item_id, no_tick))
                for tick_item_id in list_of_tick_list_items
            ]
        )
        return DictOfTicksWithItem(as_dict)

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
class CadetWithTickListItems:
    cadet_id: str
    dict_of_ticks_with_items: DictOfTicksWithItem

    def add_all_ticks_inplace(self):
        self.dict_of_ticks_with_items.add_all_ticks_inplace()

    def aligned_to_list_of_tick_list_items(self, list_of_tick_list_items: List[str]):
        return CadetWithTickListItems(
            self.cadet_id,
            dict_of_ticks_with_items=self.dict_of_ticks_with_items.aligned_to_list_of_tick_list_items(
                list_of_tick_list_items
            ),
        )

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


class ListOfCadetsWithTickListItems(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetWithTickListItems

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

    def index_of_cadet_id(self, cadet_id: str):
        list_of_ids = self.list_of_cadet_ids

        return list_of_ids.index(cadet_id)

    @property
    def list_of_cadet_ids(self):
        return [str(item.cadet_id) for item in self]

    def subset_from_list_of_cadet_ids(
        self, list_of_cadet_ids: List[str], generate_empty_row_if_missing: bool = True
    ) -> "ListOfCadetsWithTickListItems":
        ## generate empty ticksheet row for missing cadet
        new_ticksheet_list = []
        for cadet_id in list_of_cadet_ids:
            try:
                relevant_row = self[self.index_of_cadet_id(cadet_id)]
            except ValueError:
                if generate_empty_row_if_missing:
                    relevant_row = empty_row_given_non_empty_tick_list(
                        cadet_id=cadet_id, list_of_cadets_with_tick_list_items=self
                    )
                else:
                    raise Exception("Missing cadet id from ticksheet")

            new_ticksheet_list.append(relevant_row)

        return ListOfCadetsWithTickListItems(new_ticksheet_list)

    def subset_and_order_from_list_of_tick_sheet_items(
        self, list_of_tick_sheet_items: ListOfTickSheetItems
    ) -> "ListOfCadetsWithTickListItems":
        list_of_tick_sheet_item_ids = list_of_tick_sheet_items.list_of_ids
        new_tick_list = self.subset_and_order_from_list_of_item_ids(
            list_of_tick_sheet_item_ids
        )

        return new_tick_list

    def subset_and_order_from_list_of_item_ids(
        self, list_of_tick_sheet_item_ids: List[str]
    ) -> "ListOfCadetsWithTickListItems":
        new_list = [
            cadet_with_ticks.aligned_to_list_of_tick_list_items(
                list_of_tick_sheet_item_ids
            )
            for cadet_with_ticks in self
        ]

        new_tick_list = ListOfCadetsWithTickListItems(new_list)

        return new_tick_list

    def df_replacing_id_with_ordered_label_list(
        self,
        list_of_cadet_names: List[str],
        list_of_tick_item_names: List[str],
        list_of_substage_names: List[str],
        qualification_name: str = "",
        group_name: str = "",
    ) -> LabelledTickSheetWithCadetIds:
        df = self.as_df_of_str()
        list_of_cadet_ids = self.list_of_cadet_ids
        df = df.drop("cadet_id", axis=1)
        df.index = list_of_cadet_names
        df.columns = [list_of_substage_names, list_of_tick_item_names]

        return LabelledTickSheetWithCadetIds(
            df=df,
            list_of_cadet_ids=list_of_cadet_ids,
            qualification_name=qualification_name,
            group_name=group_name,
        )

    def list_of_tick_list_item_ids(self) -> List[str]:
        first_cadet = self[0]
        tick_list_items = first_cadet.list_of_tick_item_ids

        return tick_list_items

    def add_full_rows_inplace_where_cadet_has_qualifications(
        self, has_qualifications_dict: Dict[str, bool]
    ):
        for cadet_with_tick_list in self:
            if has_qualifications_dict[str(cadet_with_tick_list.cadet_id)]:
                cadet_with_tick_list.add_all_ticks_inplace()

    def add_or_modify_specific_tick_return_new_ticksheet(
        self, new_tick: Tick, cadet_id: str, item_id: str
    ) -> "ListOfCadetsWithTickListItems":
        if cadet_id in self.list_of_cadet_ids:
            return self._add_or_modify_specific_tick_where_cadet_in_existing_list(
                new_tick=new_tick, cadet_id=cadet_id, item_id=item_id
            )
        else:
            return self._add_new_cadet_with_tick(
                new_tick=new_tick, cadet_id=cadet_id, item_id=item_id
            )

    def _add_or_modify_specific_tick_where_cadet_in_existing_list(
        self, new_tick: Tick, cadet_id: str, item_id: str
    ) -> "ListOfCadetsWithTickListItems":
        new_ticksheet = self._ensure_existing_cadets_have_potentially_new_item_id(
            item_id
        )
        existing_idx = new_ticksheet.index_of_cadet_id(cadet_id)
        existing_cadet_with_tick_list_items = new_ticksheet[existing_idx]

        existing_cadet_with_tick_list_items.dict_of_ticks_with_items[item_id] = new_tick
        new_ticksheet[existing_idx] = existing_cadet_with_tick_list_items

        return new_ticksheet

    def _add_new_cadet_with_tick(
        self, new_tick: Tick, cadet_id: str, item_id: str
    ) -> "ListOfCadetsWithTickListItems":
        dict_of_ticks_with_items = DictOfTicksWithItem({item_id: new_tick})

        cadet_with_tick_list_items = CadetWithTickListItems(
            cadet_id=cadet_id, dict_of_ticks_with_items=dict_of_ticks_with_items
        )

        if len(self) == 0:
            return ListOfCadetsWithTickListItems([cadet_with_tick_list_items])

        new_ticksheet = self._ensure_existing_cadets_have_potentially_new_item_id(
            item_id
        )

        cadet_with_aligned_tick_list_items = (
            cadet_with_tick_list_items.aligned_to_list_of_tick_list_items(
                new_ticksheet.list_of_tick_list_item_ids()
            )
        )

        new_ticksheet += ListOfCadetsWithTickListItems(
            [cadet_with_aligned_tick_list_items]
        )

        return new_ticksheet

    def _ensure_existing_cadets_have_potentially_new_item_id(
        self, item_id: str
    ) -> "ListOfCadetsWithTickListItems":
        list_of_tick_list_item_ids = self.list_of_tick_list_item_ids()
        if item_id in list_of_tick_list_item_ids:
            return self

        list_of_tick_list_item_ids.append(item_id)
        list_of_tick_list_item_ids.sort()

        return self.subset_and_order_from_list_of_item_ids(list_of_tick_list_item_ids)


def empty_row_given_non_empty_tick_list(
    cadet_id: str, list_of_cadets_with_tick_list_items: ListOfCadetsWithTickListItems
) -> CadetWithTickListItems:
    try:
        assert len(list_of_cadets_with_tick_list_items) > 0
    except:
        raise Exception(
            "Can't create empty row if no values exist in current ticksheet list"
        )

    row_to_copy = list_of_cadets_with_tick_list_items[
        0
    ]  ## will only work if tick sheet exists
    dict_to_copy = row_to_copy.dict_of_ticks_with_items
    empty_dict = dict_to_copy.with_all_empty()
    return CadetWithTickListItems(
        cadet_id=cadet_id, dict_of_ticks_with_items=empty_dict
    )


def list_of_cadets_with_tick_list_items_as_df(
    list_of_cadets_with_tick_list_items: ListOfCadetsWithTickListItems,
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
) -> ListOfCadetsWithTickListItems:
    list_of_cadets_with_tick_lists = []
    for i in range(len(df)):
        row = df.iloc[i]
        cadet_with_tick_list_items = CadetWithTickListItems.from_dict_of_str(
            row.to_dict()
        )
        list_of_cadets_with_tick_lists.append(cadet_with_tick_list_items)

    return ListOfCadetsWithTickListItems(list_of_cadets_with_tick_lists)


list_of_tick_options = [no_tick, half_tick, full_tick, not_applicable_tick]

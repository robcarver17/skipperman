from copy import copy
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

import numpy as np
import pandas as pd
from app.objects.day_selectors import ListOfDaySelectors

from app.objects.constants import missing_data, arg_not_passed
from app.objects.generic import GenericSkipperManObjectWithIds, GenericListOfObjectsWithIds, GenericListOfObjects

@dataclass
class LabelledTickSheetWithCadetIds:
    df: pd.DataFrame
    list_of_cadet_ids: List[str]
    cadets_in_columns: bool = False
    qualification_name: str = ""
    group_name: str = ""


    def from_existing_replace_df(self, new_df: pd.DataFrame):
        return LabelledTickSheetWithCadetIds(
            df = new_df,
            list_of_cadet_ids=self.list_of_cadet_ids,
            cadets_in_columns=self.cadets_in_columns,
            qualification_name=self.qualification_name,
            group_name=self.group_name
        )

    def transpose(self):
        now_cadets_in_columns = not self.cadets_in_columns
        new_version = copy(self)
        new_version.df = new_version.df.transpose()
        new_version.cadets_in_columns = now_cadets_in_columns

        return new_version

    def add_attendance_data(self, attendance_data: ListOfDaySelectors):
        attendance = attendance_data.as_pd_data_frame()
        dummy_multindex = [['']*len(attendance.columns), attendance.columns]
        attendance.columns = dummy_multindex
        qual_multindex = pd.MultiIndex.from_tuples([('%s:' % self.qualification_name.upper(), '')])
        qual_row = pd.DataFrame('', index=qual_multindex, columns=self.df.columns)
        qual_column = pd.DataFrame('', index=self.df.index, columns=qual_multindex)

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
        health_multindex = pd.MultiIndex.from_tuples([('', 'Medical notes')])
        if self.cadets_in_columns:
            health_row = pd.DataFrame(health_notes, index=health_multindex, columns=self.df.columns)
            print(health_row)
            new_df = pd.concat([ self.df, health_row], axis=0)
        else:
            health_column = pd.DataFrame(health_notes, index=self.df.index, columns=health_multindex)
            print(health_column)
            new_df = pd.concat([ self.df, health_column], axis=1)

        return self.from_existing_replace_df(new_df)


    def add_qualification_and_group_header(self):
        qual_multindex = pd.MultiIndex.from_tuples([('%s:' % self.qualification_name.upper(), self.group_name)])

        if self.cadets_in_columns:
            qual_row = pd.DataFrame('', index=qual_multindex, columns=self.df.columns)
            new_df = pd.concat([ qual_row, self.df], axis=0)
        else:
            qual_column = pd.DataFrame('', index=self.df.index, columns=qual_multindex)
            new_df = pd.concat([ qual_column, self.df], axis=1)

        return self.from_existing_replace_df(new_df)

    def add_club_boat_asterix(self, list_of_club_boat_bool: List[bool]):
        new_df = copy(self.df)
        list_of_club_boat_asterix  = ["*" if yes else " " for yes in list_of_club_boat_bool]
        if self.cadets_in_columns:
            new_df.columns = [column+star for column,star in zip(new_df.columns, list_of_club_boat_asterix)]
        else:
            new_df.index = [column+star for column,star in zip(new_df.index, list_of_club_boat_asterix)]

        return self.from_existing_replace_df(new_df)


@dataclass
class TickSubStage(GenericSkipperManObjectWithIds):
    name: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name



class ListOfTickSubStages(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return TickSubStage

    def name_given_id(self, id: str) -> str:
        names = [item.name for item in self if item.id == id]

        if len(names)==0:
            return missing_data
        elif len(names)>1:
            raise Exception("Found more than one substage with same ID should be impossible")

        return names[0]

    def idx_given_name(self, name: str):
        id = self.id_given_name(name)
        return self.index_of_id(id)

    def id_given_name(self, name: str):
        id = [item.id for item in self if item.name == name]

        if len(id)==0:
            return missing_data
        elif len(id)>1:
            raise Exception("Found more than one substage with same name should be impossible")

        return str(id[0])

    def add(self, name: str):
        sub_stage = TickSubStage(name=name)
        try:
            assert name not in self.list_of_names()
        except:
            raise Exception("Can't add duplicate substage %s already exists" % name)
        sub_stage.id = self.next_id()

        self.append(sub_stage)

    def list_of_names(self):
        return [sub_stage.name for sub_stage in self]



@dataclass
class TickSheetItem(GenericSkipperManObjectWithIds):
    name: str
    stage_id: str
    substage_id: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name



class ListOfTickSheetItems(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return TickSheetItem

    def subset_for_qualification_stage_id(self, stage_id: str):
        new_list = [item for item in self if item.stage_id == stage_id]

        return ListOfTickSheetItems(new_list)

    def list_of_item_names(self) -> List[str]:
        return [item.name for item in self]

    def list_of_substage_ids(self) -> List[str]:
        return [item.substage_id for item in self]

Tick = Enum("Tick", ["Full", "Half", "NotApplicable", "NoTick"])

full_tick = Tick.Full
half_tick = Tick.Half
not_applicable_tick = Tick.NotApplicable
no_tick = Tick.NoTick

tick_strings_dict = {full_tick: "X", half_tick: "1/2", not_applicable_tick: "N A", no_tick: "[  ]"}
string_ticks_dict = {v: k for k, v in tick_strings_dict.items()}

@dataclass
class TickWithItem:
    tick_item_id: str
    tick: Tick

def tick_as_str(tick: Tick) -> str:
    return tick_strings_dict[tick]

def tick_from_str(some_str:str) -> Tick:
    return string_ticks_dict[some_str]

class DictOfTicksWithItem(dict):
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
    def from_list_of_ticks_with_items(cls, list_of_ticks_with_items: List[TickWithItem]):
        as_dict = dict([(tick_with_item.tick_item_id, tick_with_item.tick) for tick_with_item in list_of_ticks_with_items])
        return cls(as_dict)

    def aligned_to_list_of_tick_list_items(self, list_of_tick_list_items: List[str]):
        as_dict = dict([(tick_item_id, self.get(tick_item_id, no_tick)) for tick_item_id in list_of_tick_list_items])
        return DictOfTicksWithItem(as_dict)

    def as_dict_of_str_aligned_to_list_of_tick_list_items(self, list_of_tick_list_items: List[str]):
        return dict([(tick_item_id, tick_as_str(self.get(tick_item_id, no_tick))) for tick_item_id in list_of_tick_list_items])

    @classmethod
    def from_dict_of_str(cls, dict_of_str):
        as_dict_of_ticks_with_items = dict(
            [
                (tick_item_id, tick_from_str(tick_str))
                for tick_item_id, tick_str in dict_of_str.items()
            ]
        )

        return cls(as_dict_of_ticks_with_items)

CADET_ID="cadet_id"
@dataclass
class CadetWithTickListItems:
    cadet_id: str
    dict_of_ticks_with_items: DictOfTicksWithItem

    def add_all_ticks_inplace(self):
        self.dict_of_ticks_with_items.add_all_ticks_inplace()

    def aligned_to_list_of_tick_list_items(self, list_of_tick_list_items: List[str]):
        return CadetWithTickListItems(self.cadet_id,
                                      dict_of_ticks_with_items=self.dict_of_ticks_with_items.aligned_to_list_of_tick_list_items(list_of_tick_list_items))

    @property
    def list_of_tick_item_ids(self) -> List[str]:
        tick_list_items= list(self.dict_of_ticks_with_items.keys())
        return tick_list_items


    def as_dict_of_str_aligned_to_list_of_tick_list_items(self, list_of_tick_list_items: List[str]):
        cadet_id_dict = {CADET_ID: self.cadet_id}
        dict_of_ticks_with_items_as_str = self.dict_of_ticks_with_items.as_dict_of_str_aligned_to_list_of_tick_list_items(list_of_tick_list_items)
        dict_of_ticks_with_items_as_str[CADET_ID] = self.cadet_id

        return {**cadet_id_dict, **dict_of_ticks_with_items_as_str} ## merge dict

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
        return self.to_df_of_str()

    def to_df_of_str(self) -> pd.DataFrame:
        return list_of_cadets_with_tick_list_items_as_df(self)

    def append(self, __object):
        raise Exception("Can't append use add or modify specific tick")

    @classmethod
    def from_df_of_str(cls, df: pd.DataFrame):
        list_of_cadets_with_tick_list_items = from_df_to_list_of_cadets_with_tick_list_items(df)

        return cls(list_of_cadets_with_tick_list_items)

    def index_of_cadet_id(self, cadet_id:str):
        list_of_ids = self.list_of_cadet_ids

        return list_of_ids.index(cadet_id)

    @property
    def list_of_cadet_ids(self):
        return [str(item.cadet_id) for item in self]

    def subset_from_list_of_cadet_ids(self, list_of_cadet_ids: List[str], generate_empty_row_if_missing: bool = True) -> 'ListOfCadetsWithTickListItems':
        ## generate empty ticksheet row for missing cadet
        new_ticksheet_list = []
        for cadet_id in list_of_cadet_ids:
            try:
                relevant_row = self[self.index_of_cadet_id(cadet_id)]
            except ValueError:
                if generate_empty_row_if_missing:
                    relevant_row = empty_row_given_non_empty_tick_list(cadet_id=cadet_id, list_of_cadets_with_tick_list_items=self)
                else:
                    raise Exception("Missing cadet id from ticksheet")

            new_ticksheet_list.append(relevant_row)

        return ListOfCadetsWithTickListItems(new_ticksheet_list)

    def subset_and_order_from_list_of_tick_sheet_items(self, list_of_tick_sheet_items: ListOfTickSheetItems)-> 'ListOfCadetsWithTickListItems':
        list_of_tick_sheet_item_ids = list_of_tick_sheet_items.list_of_ids
        new_tick_list = self.subset_and_order_from_list_of_item_ids(list_of_tick_sheet_item_ids)

        return new_tick_list

    def subset_and_order_from_list_of_item_ids(self, list_of_tick_sheet_item_ids: List[str])-> 'ListOfCadetsWithTickListItems':
        new_list = [cadet_with_ticks.aligned_to_list_of_tick_list_items(list_of_tick_sheet_item_ids) for cadet_with_ticks in self]

        new_tick_list = ListOfCadetsWithTickListItems(new_list)

        return new_tick_list

    def df_replacing_id_with_ordered_label_list(self,
            list_of_cadet_names: List[str],
            list_of_tick_item_names: List[str],
            list_of_substage_names: List[str],
            qualification_name: str= "",
            group_name: str = ""
        ) -> LabelledTickSheetWithCadetIds:

            df = self.to_df_of_str()
            list_of_cadet_ids = self.list_of_cadet_ids
            df = df.drop("cadet_id", axis=1)
            df.index = list_of_cadet_names
            df.columns = [list_of_substage_names, list_of_tick_item_names]

            return LabelledTickSheetWithCadetIds(df=df, list_of_cadet_ids=list_of_cadet_ids, qualification_name=qualification_name, group_name=group_name)

    def list_of_tick_list_item_ids(self) -> List[str]:
        first_cadet = self[0]
        tick_list_items = first_cadet.list_of_tick_item_ids

        return tick_list_items

    def add_full_rows_inplace_where_cadet_has_qualifications(self, has_qualifications_dict: Dict[str, bool]):
        for cadet_with_tick_list in self:
            if has_qualifications_dict[str(cadet_with_tick_list.cadet_id)]:
                cadet_with_tick_list.add_all_ticks_inplace()

    def add_or_modify_specific_tick_return_new_ticksheet(self, new_tick: Tick, cadet_id: str,
                                                         item_id: str)  -> 'ListOfCadetsWithTickListItems':

        if cadet_id in self.list_of_cadet_ids:
            return self._add_or_modify_specific_tick_where_cadet_in_existing_list(new_tick=new_tick,
                                                                           cadet_id=cadet_id,
                                                                           item_id=item_id)
        else:
            return self._add_new_cadet_with_tick(new_tick=new_tick, cadet_id=cadet_id, item_id=item_id)

    def _add_or_modify_specific_tick_where_cadet_in_existing_list(self, new_tick: Tick, cadet_id: str,
                                    item_id: str)  -> 'ListOfCadetsWithTickListItems':

        new_ticksheet = self._ensure_existing_cadets_have_potentially_new_item_id(item_id)
        existing_idx = new_ticksheet.index_of_cadet_id(cadet_id)
        existing_cadet_with_tick_list_items =new_ticksheet[existing_idx]

        existing_cadet_with_tick_list_items.dict_of_ticks_with_items[item_id] = new_tick
        new_ticksheet[existing_idx] = existing_cadet_with_tick_list_items

        return new_ticksheet

    def _add_new_cadet_with_tick(self, new_tick: Tick, cadet_id: str,
                                    item_id: str)  -> 'ListOfCadetsWithTickListItems':

        new_ticksheet = self._ensure_existing_cadets_have_potentially_new_item_id(item_id)
        dict_of_ticks_with_items = DictOfTicksWithItem({item_id: new_tick})

        cadet_with_tick_list_items =CadetWithTickListItems(cadet_id=cadet_id,
                               dict_of_ticks_with_items=dict_of_ticks_with_items)

        cadet_with_aligned_tick_list_items = cadet_with_tick_list_items.aligned_to_list_of_tick_list_items(
            new_ticksheet.list_of_tick_list_item_ids()
        )

        new_ticksheet+=ListOfCadetsWithTickListItems([cadet_with_aligned_tick_list_items])

        return new_ticksheet

    def _ensure_existing_cadets_have_potentially_new_item_id(self, item_id:str) -> 'ListOfCadetsWithTickListItems':
        list_of_tick_list_item_ids = self.list_of_tick_list_item_ids()
        if item_id in list_of_tick_list_item_ids:
            return self

        list_of_tick_list_item_ids.append(item_id)
        list_of_tick_list_item_ids.sort()

        return self.subset_and_order_from_list_of_item_ids(list_of_tick_list_item_ids)

def empty_row_given_non_empty_tick_list(cadet_id: str, list_of_cadets_with_tick_list_items: ListOfCadetsWithTickListItems) -> CadetWithTickListItems:
    try:
        assert len(list_of_cadets_with_tick_list_items)>0
    except:
        raise Exception("Can't create empty row if no values exist in current ticksheet list")

    row_to_copy = list_of_cadets_with_tick_list_items[0]  ## will only work if tick sheet exists
    dict_to_copy = row_to_copy.dict_of_ticks_with_items
    empty_dict = dict_to_copy.with_all_empty()
    return CadetWithTickListItems(cadet_id=cadet_id, dict_of_ticks_with_items=empty_dict)


def list_of_cadets_with_tick_list_items_as_df(list_of_cadets_with_tick_list_items: ListOfCadetsWithTickListItems)-> pd.DataFrame:

    list_of_tick_list_items = list_of_cadets_with_tick_list_items.list_of_tick_list_item_ids()
    list_of_cadets_with_tick_list_items_as_dict_of_str = [
        cadet_with_tick_list_items.as_dict_of_str_aligned_to_list_of_tick_list_items(
            list_of_tick_list_items
        )
        for cadet_with_tick_list_items in list_of_cadets_with_tick_list_items
    ]

    return pd.DataFrame(list_of_cadets_with_tick_list_items_as_dict_of_str)




def from_df_to_list_of_cadets_with_tick_list_items(df: pd.DataFrame) -> ListOfCadetsWithTickListItems:
    list_of_cadets_with_tick_lists = []
    for i in range(len(df)):
        row = df.iloc[i]
        cadet_with_tick_list_items = CadetWithTickListItems.from_dict_of_str(row.to_dict())
        list_of_cadets_with_tick_lists.append(cadet_with_tick_list_items)

    return ListOfCadetsWithTickListItems(list_of_cadets_with_tick_lists)


list_of_tick_options = [no_tick, half_tick, full_tick, not_applicable_tick]

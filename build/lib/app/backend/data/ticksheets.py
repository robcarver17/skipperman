from typing import List

import pandas as pd
from app.backend.data.qualification import QualificationData

from app.objects.events import Event

from app.objects.groups import Group

from app.data_access.storage_layer.api import DataLayer
from app.objects.ticks import ListOfCadetsWithTickListItems, ListOfTickSheetItems, LabelledTickSheetWithCadetIds, Tick
from app.backend.data.group_allocations import GroupAllocationsData
from app.backend.data.cadets import CadetData
from app.backend.data.cadets_at_event import CadetsAtEventData
from app.backend.data.dinghies import DinghiesData
from app.objects.ticks import CadetWithTickListItems



class TickSheetsData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def add_or_modify_specific_tick(self, new_tick: Tick, cadet_id: str,
                                    item_id: str):

        full_tick_sheet = self.get_list_of_cadets_with_tick_list_items_for_list_of_cadets([cadet_id])
        full_tick_sheet = full_tick_sheet.add_or_modify_specific_tick_return_new_ticksheet(cadet_id=cadet_id, item_id=item_id, new_tick=new_tick)
        self.save_list_of_cadets_with_tick_list_items(full_tick_sheet)


    def list_of_substage_names_give_list_of_tick_sheet_items(self, list_of_tick_sheet_items: ListOfTickSheetItems):
        list_of_substage_ids = list_of_tick_sheet_items.list_of_substage_ids()

        return self.list_of_substage_names_given_list_of_ids(list_of_substage_ids)

    def list_of_substage_names_given_list_of_ids(self, list_of_substage_ids: List[str]):
        list_of_tick_sub_stages = self.data_api.get_list_of_tick_sub_stages()
        list_of_names = [list_of_tick_sub_stages.name_given_id(id) for id in list_of_substage_ids]

        return list_of_names

    def list_of_tick_sheet_items_for_this_qualification(self, qualification_stage_id: str) -> ListOfTickSheetItems:
        list_of_tick_sheet_items = self.data_api.get_list_of_tick_sheet_items()
        list_of_tick_sheet_items_for_this_qualification = list_of_tick_sheet_items.subset_for_qualification_stage_id(qualification_stage_id)

        return list_of_tick_sheet_items_for_this_qualification

    def add_full_rows_where_cadet_has_qualifications(self,  tick_sheet: ListOfCadetsWithTickListItems, qualification_stage_id: str) -> ListOfCadetsWithTickListItems:
        list_of_cadet_ids = tick_sheet.list_of_cadet_ids
        has_qualifications_dict = dict([(cadet_id,
                                    self.qualification_data.does_cadet_id_have_qualification(cadet_id=cadet_id, qualification_id=qualification_stage_id))
                                    for cadet_id in list_of_cadet_ids])

        tick_sheet.add_full_rows_inplace_where_cadet_has_qualifications(has_qualifications_dict)

        return tick_sheet


    def add_attendance_data(self,  event: Event, group: Group, labelled_ticksheet:LabelledTickSheetWithCadetIds) -> LabelledTickSheetWithCadetIds:
        list_of_cadet_ids = labelled_ticksheet.list_of_cadet_ids
        attendance_data = self.group_allocation_data.get_joint_attendance_matrix_for_cadet_ids_in_group_at_event(event=event,
                                                                                                                 list_of_cadet_ids=list_of_cadet_ids,
                                                                                                                 group=group)

        labelled_tick_sheet = labelled_ticksheet.add_attendance_data(attendance_data)

        return labelled_tick_sheet

    def add_medical_notes(self,  event: Event, labelled_ticksheet:LabelledTickSheetWithCadetIds) -> LabelledTickSheetWithCadetIds:
        list_of_cadet_ids = labelled_ticksheet.list_of_cadet_ids
        health_notes = self.cadets_at_event_data.get_health_notes_for_list_of_cadet_ids_at_event(event=event, list_of_cadet_ids=list_of_cadet_ids)

        labelled_tick_sheet = labelled_ticksheet.add_health_notes(health_notes)

        return labelled_tick_sheet


    def add_club_boats(self, event: Event, labelled_ticksheet:LabelledTickSheetWithCadetIds) -> LabelledTickSheetWithCadetIds:
        list_of_club_boat_bool = self.club_dinghies.list_of_club_dinghies_bool_for_list_of_cadet_ids(list_of_cadet_ids=labelled_ticksheet.list_of_cadet_ids, event=event)

        labelled_tick_sheet = labelled_ticksheet.add_club_boat_asterix(list_of_club_boat_bool)

        return labelled_tick_sheet

    def get_list_of_cadets_with_tick_list_items_for_list_of_cadets(self, list_of_cadet_ids: List[str]) -> ListOfCadetsWithTickListItems:
        list_of_all_ticks = []
        for cadet_id in list_of_cadet_ids:
            ticks_this_cadet = self.get_list_of_cadets_with_tick_list_items_for_cadet_id(cadet_id)
            list_of_all_ticks+=ticks_this_cadet

        return ListOfCadetsWithTickListItems(list_of_all_ticks)

    def get_list_of_cadets_with_tick_list_items_for_cadet_id(self, cadet_id) -> ListOfCadetsWithTickListItems:
        return self.data_api.get_list_of_cadets_with_tick_list_items_for_cadet_id(cadet_id=cadet_id)


    def save_list_of_cadets_with_tick_list_items(self, list_of_cadets_with_tick_list_items: ListOfCadetsWithTickListItems):
        self.data_api.save_list_of_cadets_with_tick_list_items_for_cadet_id(list_of_cadets_with_tick_list_items)

    @property
    def qualification_data(self) ->  QualificationData:
        return QualificationData(self.data_api)

    @property
    def group_allocation_data(self) -> GroupAllocationsData:
        return GroupAllocationsData(data_api=self.data_api)

    @property
    def cadet_data(self)-> CadetData:
        return CadetData(data_api=self.data_api)

    @property
    def cadets_at_event_data(self) -> CadetsAtEventData:
        return CadetsAtEventData(data_api=self.data_api)

    @property
    def club_dinghies(self) -> DinghiesData:
        return DinghiesData(data_api=self.data_api)
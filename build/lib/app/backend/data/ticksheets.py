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
from app.backend.data.resources import ClubDinghiesData
from app.objects.ticks import CadetWithTickListItems



class TickSheetsData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def add_or_modify_specific_tick(self, new_tick: Tick, cadet_id: str,
                                    item_id: str):

        full_tick_sheet = self.get_list_of_cadets_with_tick_list_items()
        full_tick_sheet = full_tick_sheet.add_or_modify_specific_tick_return_new_ticksheet(cadet_id=cadet_id, item_id=item_id, new_tick=new_tick)
        self.save_list_of_cadets_with_tick_list_items(full_tick_sheet)

    def get_labelled_ticksheet_df_for_group_at_event(self,event: Event,
                                                     group: Group,
                                                        qualification_stage_id: str,
                                                     include_attendance_columns: bool = True,
                                                     add_header: bool = True,
                                                     sailors_in_columns:bool = True,
                                                     asterix_club_boats: bool = True,
                                                     medical_notes: bool = True) -> LabelledTickSheetWithCadetIds:



        labelled_ticksheet = self.get_labelled_ticksheet_df_for_cadets_in_group_at_event_for_qualification(event=event,
                                                                                                           qualification_stage_id=qualification_stage_id,
                                                                                                           group=group)

        if add_header:
            labelled_ticksheet = labelled_ticksheet.add_qualification_and_group_header()
        if include_attendance_columns:
            labelled_ticksheet = self.add_attendance_data(event=event, labelled_ticksheet=labelled_ticksheet)
        if asterix_club_boats:
            labelled_ticksheet = self.add_club_boats(event=event, labelled_ticksheet=labelled_ticksheet)
        if medical_notes:
            labelled_ticksheet = self.add_medical_notes(event=event, labelled_ticksheet=labelled_ticksheet)

        if sailors_in_columns:
            labelled_ticksheet = labelled_ticksheet.transpose()


        return labelled_ticksheet

    def get_labelled_ticksheet_df_for_cadets_in_group_at_event_for_qualification(self, event: Event,
                                                                                 group: Group,
                                                                                 qualification_stage_id: str) -> LabelledTickSheetWithCadetIds:

        tick_sheet = self.get_ticksheet_for_cadets_in_group_at_event_for_qualification(event=event, group=group, qualification_stage_id=qualification_stage_id)

        ordered_list_of_cadet_ids = tick_sheet.list_of_cadet_ids

        list_of_cadet_names_for_subset = self.cadet_data.get_list_of_cadet_names_given_list_of_cadet_ids(ordered_list_of_cadet_ids)

        list_of_tick_sheet_items_for_this_qualification = self.list_of_tick_sheet_items_for_this_qualification(
            qualification_stage_id)
        list_of_tick_item_names = list_of_tick_sheet_items_for_this_qualification.list_of_item_names()
        list_of_substage_names = self.list_of_substage_names_give_list_of_tick_sheet_items(list_of_tick_sheet_items_for_this_qualification)

        qualification_name = self.data_api.get_list_of_qualifications().name_given_id(qualification_stage_id)
        group_name = group.group_name

        labelled_ticksheet= tick_sheet.df_replacing_id_with_ordered_label_list(
            list_of_cadet_names = list_of_cadet_names_for_subset,
            list_of_tick_item_names = list_of_tick_item_names,
            list_of_substage_names = list_of_substage_names,
            qualification_name=qualification_name,
            group_name=group_name
        )

        return labelled_ticksheet

    def get_ticksheet_for_cadets_in_group_at_event_for_qualification(self, event: Event,
                                                                     group: Group,
                                                                     qualification_stage_id: str) -> ListOfCadetsWithTickListItems:

        list_of_cadet_ids = self.group_allocation_data.list_of_cadet_ids_in_a_specific_group_if_cadet_active_at_event(event=event, group=group)

        full_tick_sheet = self.get_list_of_cadets_with_tick_list_items()
        list_of_tick_sheet_items_for_this_qualification = self.list_of_tick_sheet_items_for_this_qualification(qualification_stage_id)
        ordered_list_of_cadet_ids = self.cadet_data.reorder_list_of_cadet_ids_by_cadet_name(list_of_cadet_ids)

        ## generate empty ticksheet row for missing cadet
        tick_sheet = full_tick_sheet.subset_from_list_of_cadet_ids(ordered_list_of_cadet_ids, generate_empty_row_if_missing=True)
        tick_sheet = tick_sheet.subset_and_order_from_list_of_tick_sheet_items(list_of_tick_sheet_items_for_this_qualification)
        tick_sheet = self.add_full_rows_where_cadet_has_qualifications(tick_sheet, qualification_stage_id=qualification_stage_id)

        return tick_sheet



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


    def add_attendance_data(self,  event: Event, labelled_ticksheet:LabelledTickSheetWithCadetIds) -> LabelledTickSheetWithCadetIds:
        list_of_cadet_ids = labelled_ticksheet.list_of_cadet_ids
        attendance_data = self.cadets_at_event_data.get_attendance_matrix_for_list_of_cadet_ids_at_event(event=event, list_of_cadet_ids=list_of_cadet_ids)

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

    def get_list_of_cadets_with_tick_list_items(self) -> ListOfCadetsWithTickListItems:
        return self.data_api.get_list_of_cadets_with_tick_list_items()


    def save_list_of_cadets_with_tick_list_items(self, list_of_cadets_with_tick_list_items: ListOfCadetsWithTickListItems):
        self.data_api.save_list_of_cadets_with_tick_list_items(list_of_cadets_with_tick_list_items)

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
    def club_dinghies(self) -> ClubDinghiesData:
        return ClubDinghiesData(data_api=self.data_api)
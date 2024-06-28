from typing import List

from app.objects.constants import missing_data

from app.objects.qualifications import Qualification

from app.backend.data.qualification import QualificationData

from app.objects.events import Event

from app.objects.groups import Group

from app.data_access.storage_layer.api import DataLayer
from app.objects.ticks import (
    ListOfCadetsWithTickListItems,
    ListOfTickSheetItems,
    LabelledTickSheetWithCadetIds,
    Tick,
    QualificationsAndTickItemsAsDict,
    TickSubStagesAsDict,
    ListOfTickSubStages,
    TickSubStage, TickSheetItem,
)
from app.backend.data.group_allocations import GroupAllocationsData
from app.backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.backend.data.dinghies import DinghiesData


class TickSheetsData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def modify_ticksheet_item_name(self,
                                              existing_tick_item: TickSheetItem,
                         new_item_name: str):

        list_of_tick_sheet_items = self.data_api.get_list_of_tick_sheet_items()
        list_of_tick_sheet_items.modify_ticksheet_item_name(tick_item_id = existing_tick_item.id,
                                                            new_item_name=new_item_name)
        self.data_api.save_list_of_tick_sheet_items(list_of_tick_sheet_items)


    def modify_substage_name(self,
                             existing_substage: TickSubStage,
                             qualification: Qualification,
                             new_name: str):

        ## possibilies: - only this qualification has this substage - modify underlying name
        ##             - there exists a qualification with the same name - replace all instances of the current substage/stage combination with the new one
        ##              - neithier - create a new substage and replace all instances of the current substage/stage combination with the new one

        only_this_qualification_has_this_substage = self.only_this_qualification_has_this_substage(
            substage = existing_substage,
            qualification=qualification
        )

        if only_this_qualification_has_this_substage:
            print("it's unqiue")

            self.modify_name_of_substage_unique_to_qualification(qualification=qualification, existing_substage=existing_substage,
                                                                 new_name=new_name)
            return

        ##             - there exists a qualification with the same name - replace all instances of the current substage/stage combination with the new one
        ##              - neithier - create a new substage and replace all instances of the current substage/stage combination with the new one

        new_substage_id = self.get_substage_id_for_name_adding_if_missing(new_name)
        print("substage id %s" % new_substage_id)
        self.switch_all_instances_of_substage_for_qualification(
            existing_substage_id=existing_substage.id,
            new_substage_id=new_substage_id,
            qualification_id=qualification.id
        )

    def only_this_qualification_has_this_substage(self, substage: TickSubStage,
                             qualification: Qualification) -> bool:

        list_of_tick_sheet_items = self.data_api.get_list_of_tick_sheet_items()
        return list_of_tick_sheet_items.only_this_qualification_has_this_substage(substage_id = substage.id,
                                                                                  stage_id = qualification.id)

    def modify_name_of_substage_unique_to_qualification(self, qualification: Qualification, existing_substage: TickSubStage,
                             new_name: str):
        new_name_exists = self.does_substage_name_exist(new_name)
        if new_name_exists:
            self.modify_name_of_substage_unique_to_qualification_where_new_name_already_exists(
                qualification=qualification,
                existing_substage=existing_substage,
                new_name=new_name
            )
        else:
            self.modify_name_of_substage_unique_to_qualification_where_new_name_also_does_not_exist(
                existing_substage=existing_substage,
                new_name=new_name
            )

    def does_substage_name_exist(self, substage_name: str):
        list_of_substages =self.data_api.get_list_of_tick_sub_stages()
        return list_of_substages.idx_given_name(substage_name) is not missing_data

    def modify_name_of_substage_unique_to_qualification_where_new_name_already_exists(self, qualification: Qualification, existing_substage: TickSubStage,
                                                            new_name: str):

        list_of_substages =self.data_api.get_list_of_tick_sub_stages()
        existing_idx = list_of_substages.index_of_id(existing_substage.id)
        new_substage_id = list_of_substages.id_given_name(new_name)
        list_of_substages.pop(existing_idx)

        self.switch_all_instances_of_substage_for_qualification(
            qualification_id=qualification.id,
            existing_substage_id=existing_substage.id,
            new_substage_id=new_substage_id
        )

        self.data_api.save_list_of_tick_sub_stages(list_of_substages)


    def modify_name_of_substage_unique_to_qualification_where_new_name_also_does_not_exist(self, existing_substage: TickSubStage,
                                                            new_name: str):

        list_of_substages =self.data_api.get_list_of_tick_sub_stages()
        list_of_substages.modify_name_of_substage_where_new_name_also_does_not_exist(substage_id=existing_substage.id,
                                                  new_name=new_name)
        self.data_api.save_list_of_tick_sub_stages(list_of_substages)

    def switch_all_instances_of_substage_for_qualification(self, existing_substage_id: str,
                             qualification_id: str,
                             new_substage_id: str):

        list_of_tick_sheet_items = self.data_api.get_list_of_tick_sheet_items()
        list_of_tick_sheet_items.switch_all_instances_of_substage_for_qualification(stage_id=qualification_id,
                                                                                    existing_substage_id=existing_substage_id,
                                                                                    new_substage_id=new_substage_id)
        self.data_api.save_list_of_tick_sheet_items(list_of_tick_sheet_items)

    def add_new_ticklistitem_to_qualification(self, qualification: Qualification,
                                              substage: TickSubStage, new_tick_list_name: str):
        list_of_tick_sheet_items = self.data_api.get_list_of_tick_sheet_items()
        list_of_tick_sheet_items.add(
            name=new_tick_list_name,
            stage_id=qualification.id,
            substage_id=substage.id
        )

        self.data_api.save_list_of_tick_sheet_items(list_of_tick_sheet_items)

    def add_new_substage_to_qualification(self, qualification: Qualification, new_substage_name: str):
        substage_id = self.get_substage_id_for_name_adding_if_missing(new_substage_name)
        list_of_tick_sheet_items = self.data_api.get_list_of_tick_sheet_items()
        list_of_tick_sheet_items.add_placeholder(stage_id=qualification.id, substage_id=substage_id)
        self.data_api.save_list_of_tick_sheet_items(list_of_tick_sheet_items)

    def get_substage_id_for_name_adding_if_missing(self,  new_substage_name: str) -> str:
        ## check to see if exists
        list_of_substages =self.data_api.get_list_of_tick_sub_stages()
        substage_id = list_of_substages.id_given_name(new_substage_name)
        if substage_id is missing_data:
            list_of_substages.add(new_substage_name)
            self.data_api.save_list_of_tick_sub_stages(list_of_substages)
            substage_id = list_of_substages.id_given_name(new_substage_name)

        return substage_id

    def add_or_modify_specific_tick(self, new_tick: Tick, cadet_id: str, item_id: str):
        full_tick_sheet = (
            self.get_list_of_cadets_with_tick_list_items_for_list_of_cadets([cadet_id])
        )
        full_tick_sheet = (
            full_tick_sheet.add_or_modify_specific_tick_return_new_ticksheet(
                cadet_id=cadet_id, item_id=item_id, new_tick=new_tick
            )
        )
        self.save_list_of_cadets_with_tick_list_items(full_tick_sheet)

    def list_of_substage_names_give_list_of_tick_sheet_items(
        self, list_of_tick_sheet_items: ListOfTickSheetItems
    ):
        list_of_substage_ids = list_of_tick_sheet_items.list_of_substage_ids()

        return self.list_of_substage_names_given_list_of_ids(list_of_substage_ids)

    def list_of_substage_names_given_list_of_ids(self, list_of_substage_ids: List[str]):
        subset_list_of_tick_sub_stages = self.list_of_substages_given_list_of_ids(
            list_of_substage_ids
        )
        return subset_list_of_tick_sub_stages.list_of_names()

    def list_of_substages_given_list_of_tick_sheet_items(
        self, list_of_tick_sheet_items: ListOfTickSheetItems
    ) -> ListOfTickSubStages:
        list_of_substage_ids = list_of_tick_sheet_items.list_of_substage_ids()
        return self.list_of_substages_given_list_of_ids(list_of_substage_ids)

    def list_of_substages_given_list_of_ids(
        self, list_of_substage_ids: List[str]
    ) -> ListOfTickSubStages:
        list_of_tick_sub_stages = self.data_api.get_list_of_tick_sub_stages()
        return ListOfTickSubStages.subset_from_list_of_ids(
            list_of_tick_sub_stages, list_of_ids=list_of_substage_ids
        )

    def qualifications_and_tick_items_as_dict(self) -> QualificationsAndTickItemsAsDict:
        list_of_qualifications = self.qualification_data.load_list_of_qualifications()
        list_of_tick_sheet_items = self.data_api.get_list_of_tick_sheet_items()

        items_as_dict = dict(
            [
                (
                    qualification,
                    self.tick_substages_as_dict_for_qualification_give_list_of_ticksheet_items(
                        qualification=qualification,
                        list_of_tick_sheet_items=list_of_tick_sheet_items,
                    ),
                )
                for qualification in list_of_qualifications
            ]
        )

        return QualificationsAndTickItemsAsDict(items_as_dict)

    def tick_substages_as_dict_for_qualification_give_list_of_ticksheet_items(
        self,
        qualification: Qualification,
        list_of_tick_sheet_items: ListOfTickSheetItems,
    ) -> TickSubStagesAsDict:
        list_of_tick_sheet_items_for_qualification = (
            list_of_tick_sheet_items.subset_for_qualification_stage_id(qualification.id, ignore_placeholders=False)

        )
        list_of_substages = self.list_of_substages_given_list_of_tick_sheet_items(
            list_of_tick_sheet_items_for_qualification
        )

        items_as_dict = dict(
            [
                (
                    substage,
                    self.list_of_ticksheet_items_for_substage_given_list_of_ticksheet_items_for_qualification(
                        substage=substage,
                        list_of_tick_sheet_items_for_qualification=list_of_tick_sheet_items_for_qualification,
                    ),
                )
                for substage in list_of_substages
            ]
        )

        return TickSubStagesAsDict(items_as_dict)

    def list_of_ticksheet_items_for_substage_given_list_of_ticksheet_items_for_qualification(
        self,
        substage: TickSubStage,
        list_of_tick_sheet_items_for_qualification: ListOfTickSheetItems,
    ) -> ListOfTickSheetItems:
        return list_of_tick_sheet_items_for_qualification.subset_for_substage_id_ignoring_placeholders(
            substage_id=substage.id
        )

    def list_of_tick_sheet_items_for_this_qualification(
        self, qualification_stage_id: str
    ) -> ListOfTickSheetItems:
        list_of_tick_sheet_items = self.data_api.get_list_of_tick_sheet_items()
        list_of_tick_sheet_items_for_this_qualification = (
            list_of_tick_sheet_items.subset_for_qualification_stage_id(
                qualification_stage_id,
                ignore_placeholders=True
            )
        )

        return list_of_tick_sheet_items_for_this_qualification

    def add_full_rows_where_cadet_has_qualifications(
        self, tick_sheet: ListOfCadetsWithTickListItems, qualification_stage_id: str
    ) -> ListOfCadetsWithTickListItems:
        list_of_cadet_ids = tick_sheet.list_of_cadet_ids
        has_qualifications_dict = dict(
            [
                (
                    cadet_id,
                    self.qualification_data.does_cadet_id_have_qualification(
                        cadet_id=cadet_id, qualification_id=qualification_stage_id
                    ),
                )
                for cadet_id in list_of_cadet_ids
            ]
        )

        tick_sheet.add_full_rows_inplace_where_cadet_has_qualifications(
            has_qualifications_dict
        )

        return tick_sheet

    def add_attendance_data(
        self,
        event: Event,
        group: Group,
        labelled_ticksheet: LabelledTickSheetWithCadetIds,
    ) -> LabelledTickSheetWithCadetIds:
        list_of_cadet_ids = labelled_ticksheet.list_of_cadet_ids
        attendance_data = self.group_allocation_data.get_joint_attendance_matrix_for_cadet_ids_in_group_at_event(
            event=event, list_of_cadet_ids=list_of_cadet_ids, group=group
        )

        labelled_tick_sheet = labelled_ticksheet.add_attendance_data(attendance_data)

        return labelled_tick_sheet

    def add_medical_notes(
        self, event: Event, labelled_ticksheet: LabelledTickSheetWithCadetIds
    ) -> LabelledTickSheetWithCadetIds:
        list_of_cadet_ids = labelled_ticksheet.list_of_cadet_ids
        health_notes = (
            self.cadets_at_event_data.get_health_notes_for_list_of_cadet_ids_at_event(
                event=event, list_of_cadet_ids=list_of_cadet_ids
            )
        )

        labelled_tick_sheet = labelled_ticksheet.add_health_notes(health_notes)

        return labelled_tick_sheet

    def add_club_boats(
        self, event: Event, labelled_ticksheet: LabelledTickSheetWithCadetIds
    ) -> LabelledTickSheetWithCadetIds:
        list_of_club_boat_bool = (
            self.club_dinghies.list_of_club_dinghies_bool_for_list_of_cadet_ids(
                list_of_cadet_ids=labelled_ticksheet.list_of_cadet_ids, event=event
            )
        )

        labelled_tick_sheet = labelled_ticksheet.add_club_boat_asterix(
            list_of_club_boat_bool
        )

        return labelled_tick_sheet

    def get_list_of_cadets_with_tick_list_items_for_list_of_cadets(
        self, list_of_cadet_ids: List[str]
    ) -> ListOfCadetsWithTickListItems:
        list_of_all_ticks = []
        for cadet_id in list_of_cadet_ids:
            ticks_this_cadet = (
                self.get_list_of_cadets_with_tick_list_items_for_cadet_id(cadet_id)
            )
            list_of_all_ticks += ticks_this_cadet

        return ListOfCadetsWithTickListItems(list_of_all_ticks)

    def get_list_of_cadets_with_tick_list_items_for_cadet_id(
        self, cadet_id
    ) -> ListOfCadetsWithTickListItems:
        return self.data_api.get_list_of_cadets_with_tick_list_items_for_cadet_id(
            cadet_id=cadet_id
        )

    def save_list_of_cadets_with_tick_list_items(
        self, list_of_cadets_with_tick_list_items: ListOfCadetsWithTickListItems
    ):
        self.data_api.save_list_of_cadets_with_tick_list_items_for_cadet_id(
            list_of_cadets_with_tick_list_items
        )

    @property
    def qualification_data(self) -> QualificationData:
        return QualificationData(self.data_api)

    @property
    def group_allocation_data(self) -> GroupAllocationsData:
        return GroupAllocationsData(data_api=self.data_api)

    @property
    def cadets_at_event_data(self) -> CadetsAtEventIdLevelData:
        return CadetsAtEventIdLevelData(data_api=self.data_api)

    @property
    def club_dinghies(self) -> DinghiesData:
        return DinghiesData(data_api=self.data_api)

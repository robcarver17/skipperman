from typing import Dict, List

from app.objects.exceptions import missing_data
from app.objects.qualifications import Qualification, ListOfQualifications
from app.objects.substages import (
    TickSubStage,
    ListOfTickSubStages,
    TickSheetItem,
    ListOfTickSheetItems,
)


class TickSubStagesAsDict(Dict[TickSubStage, ListOfTickSheetItems]):
    def substage_names(self):
        list_of_substages = list(self.keys())
        return [substage.name for substage in list_of_substages]

    @property
    def list_of_tick_sheet_items_for_this_qualification(self) -> ListOfTickSheetItems:
        list_of_items = []
        for list_of_tick_sheet_items_for_substage in self.values():
            list_of_items += list_of_tick_sheet_items_for_substage

        return ListOfTickSheetItems(list_of_items)

    @property
    def list_of_substage_names_aligned_to_tick_sheet_items(self) -> List[str]:
        all_substage_names = []
        for tick_substage, dict_of_tick_sheet_items in self.items():
            all_substage_names += [tick_substage.name] * len(dict_of_tick_sheet_items)

        return all_substage_names


class QualificationsAndTickItemsAsDict(Dict[Qualification, TickSubStagesAsDict]):
    def __init__(
        self,
        list_of_qualifications: ListOfQualifications,
        list_of_tick_sheet_items: ListOfTickSheetItems,
        list_of_tick_sub_stages: ListOfTickSubStages,
    ):
        dict_of_items = (
            create_raw_qualifications_and_tick_items_as_dict_from_underyling(
                list_of_qualifications=list_of_qualifications,
                list_of_tick_sub_stages=list_of_tick_sub_stages,
                list_of_tick_sheet_items=list_of_tick_sheet_items,
            )
        )
        super().__init__(dict_of_items)
        self.list_of_qualifications = list_of_qualifications
        self.list_of_tick_sub_stages = list_of_tick_sub_stages
        self.list_of_tick_sheet_items = list_of_tick_sheet_items

    def list_of_substage_names(self):
        list_of_substage_names = []
        for tick_substages_dict in self.values():
            substage_names = tick_substages_dict.substage_names()
            list_of_substage_names += substage_names

        return list(set(list_of_substage_names))

    def add_new_ticklistitem_to_qualification(
        self,
        qualification: Qualification,
        substage: TickSubStage,
        new_tick_list_name: str,
    ):
        list_of_tick_sheet_items = self.list_of_tick_sheet_items
        list_of_tick_sheet_items.add(
            name=new_tick_list_name, stage_id=qualification.id, substage_id=substage.id
        )

    def modify_substage_name(
        self,
        existing_substage: TickSubStage,
        qualification: Qualification,
        new_name: str,
    ):
        ## possibilies: - only this qualification has this substage - modify underlying name
        ##             - there exists a qualification with the same name - replace all instances of the current substage/stage combination with the new one
        ##              - neithier - create a new substage and replace all instances of the current substage/stage combination with the new one

        only_this_qualification_has_this_substage = (
            self.only_this_qualification_has_this_substage(
                substage=existing_substage, qualification=qualification
            )
        )

        if only_this_qualification_has_this_substage:
            print("it's unqiue")

            self.modify_name_of_substage_unique_to_qualification(
                qualification=qualification,
                existing_substage=existing_substage,
                new_name=new_name,
            )
            return

        ##             - there exists a qualification with the same name - replace all instances of the current substage/stage combination with the new one
        ##              - neithier - create a new substage and replace all instances of the current substage/stage combination with the new one

        new_substage_id = self.get_substage_id_for_name_adding_if_missing(new_name)
        print("substage id %s" % new_substage_id)
        self.switch_all_instances_of_substage_for_qualification(
            existing_substage_id=existing_substage.id,
            new_substage_id=new_substage_id,
            qualification_id=qualification.id,
        )

    def only_this_qualification_has_this_substage(
        self, substage: TickSubStage, qualification: Qualification
    ) -> bool:
        list_of_tick_sheet_items = self.list_of_tick_sheet_items
        return list_of_tick_sheet_items.only_this_qualification_has_this_substage(
            substage_id=substage.id, stage_id=qualification.id
        )

    def modify_name_of_substage_unique_to_qualification(
        self,
        qualification: Qualification,
        existing_substage: TickSubStage,
        new_name: str,
    ):
        new_name_exists = self.does_substage_name_exist(new_name)
        if new_name_exists:
            self.modify_name_of_substage_unique_to_qualification_where_new_name_already_exists(
                qualification=qualification,
                existing_substage=existing_substage,
                new_name=new_name,
            )
        else:
            self.modify_name_of_substage_unique_to_qualification_where_new_name_also_does_not_exist(
                existing_substage=existing_substage, new_name=new_name
            )

    def does_substage_name_exist(self, substage_name: str):
        list_of_substages = self.list_of_tick_sub_stages
        return list_of_substages.idx_given_name(substage_name) is not missing_data

    def modify_name_of_substage_unique_to_qualification_where_new_name_already_exists(
        self,
        qualification: Qualification,
        existing_substage: TickSubStage,
        new_name: str,
    ):
        list_of_substages = self.list_of_tick_sub_stages
        existing_idx = list_of_substages.index_of_id(existing_substage.id)
        new_substage_id = list_of_substages.id_given_name(new_name)
        list_of_substages.pop(existing_idx)

        self.switch_all_instances_of_substage_for_qualification(
            qualification_id=qualification.id,
            existing_substage_id=existing_substage.id,
            new_substage_id=new_substage_id,
        )

    def modify_name_of_substage_unique_to_qualification_where_new_name_also_does_not_exist(
        self, existing_substage: TickSubStage, new_name: str
    ):
        list_of_substages = self.list_of_tick_sub_stages
        list_of_substages.modify_name_of_substage_where_new_name_also_does_not_exist(
            substage_id=existing_substage.id, new_name=new_name
        )

    def switch_all_instances_of_substage_for_qualification(
        self, existing_substage_id: str, qualification_id: str, new_substage_id: str
    ):
        list_of_tick_sheet_items = self.list_of_tick_sheet_items
        list_of_tick_sheet_items.switch_all_instances_of_substage_for_qualification(
            stage_id=qualification_id,
            existing_substage_id=existing_substage_id,
            new_substage_id=new_substage_id,
        )

    def modify_ticksheet_item_name(
        self, existing_tick_item: TickSheetItem, new_item_name: str
    ):
        list_of_tick_sheet_items = self.list_of_tick_sheet_items
        list_of_tick_sheet_items.modify_ticksheet_item_name(
            tick_item_id=existing_tick_item.id, new_item_name=new_item_name
        )
        self.list_of_tick_sheet_items = list_of_tick_sheet_items

    def add_new_substage_to_qualification(
        self, qualification: Qualification, new_substage_name: str
    ):
        substage_id = self.get_substage_id_for_name_adding_if_missing(new_substage_name)
        list_of_tick_sheet_items = self.list_of_tick_sheet_items
        list_of_tick_sheet_items.add_placeholder(
            stage_id=qualification.id, substage_id=substage_id
        )
        self.list_of_tick_sheet_items = list_of_tick_sheet_items

    def get_substage_id_for_name_adding_if_missing(self, new_substage_name: str) -> str:
        ## check to see if exists
        list_of_substages = self.list_of_tick_sub_stages
        substage_id = list_of_substages.id_given_name(new_substage_name)
        if substage_id is missing_data:
            list_of_substages.add(new_substage_name)
            self.list_of_tick_sub_stages = list_of_substages
            substage_id = list_of_substages.id_given_name(new_substage_name)

        return substage_id

    @property
    def list_of_tick_sheet_items(self) -> ListOfTickSheetItems:
        return self._list_of_tick_sheet_items

    @property
    def list_of_qualifications(self) -> ListOfQualifications:
        return self._list_of_qualifications

    @property
    def list_of_tick_sub_stages(self) -> ListOfTickSubStages:
        return self._list_of_tick_sub_stages

    @list_of_qualifications.setter
    def list_of_qualifications(self, list_of_qualifications: ListOfQualifications):
        self._list_of_qualifications = list_of_qualifications

    @list_of_tick_sheet_items.setter
    def list_of_tick_sheet_items(self, list_of_tick_sheet_items: ListOfTickSheetItems):
        self._list_of_tick_sheet_items = list_of_tick_sheet_items

    @list_of_tick_sub_stages.setter
    def list_of_tick_sub_stages(self, list_of_tick_sub_stages: ListOfTickSubStages):
        self._list_of_tick_sub_stages = list_of_tick_sub_stages


def create_qualifications_and_tick_items_as_dict_from_underyling(
    list_of_qualifications: ListOfQualifications,
    list_of_tick_sheet_items: ListOfTickSheetItems,
    list_of_tick_sub_stages: ListOfTickSubStages,
) -> QualificationsAndTickItemsAsDict:
    return QualificationsAndTickItemsAsDict(
        list_of_qualifications=list_of_qualifications,
        list_of_tick_sheet_items=list_of_tick_sheet_items,
        list_of_tick_sub_stages=list_of_tick_sub_stages,
    )


def create_raw_qualifications_and_tick_items_as_dict_from_underyling(
    list_of_qualifications: ListOfQualifications,
    list_of_tick_sheet_items: ListOfTickSheetItems,
    list_of_tick_sub_stages: ListOfTickSubStages,
) -> Dict[Qualification, TickSubStagesAsDict]:
    items_as_dict = dict(
        [
            (
                qualification,
                tick_substages_as_dict_for_qualification_give_list_of_ticksheet_items(
                    qualification=qualification,
                    list_of_tick_sheet_items=list_of_tick_sheet_items,
                    list_of_tick_sub_stages=list_of_tick_sub_stages,
                ),
            )
            for qualification in list_of_qualifications
        ]
    )

    return items_as_dict


def tick_substages_as_dict_for_qualification_give_list_of_ticksheet_items(
    list_of_tick_sub_stages: ListOfTickSubStages,
    qualification: Qualification,
    list_of_tick_sheet_items: ListOfTickSheetItems,
) -> TickSubStagesAsDict:
    list_of_tick_sheet_items_for_qualification = (
        list_of_tick_sheet_items.subset_for_qualification_stage_id(
            qualification.id, ignore_placeholders=False
        )
    )
    list_of_substages = list_of_substages_given_list_of_tick_sheet_items(
        list_of_tick_sheet_items=list_of_tick_sheet_items_for_qualification,
        list_of_tick_sub_stages=list_of_tick_sub_stages,
    )

    items_as_dict = dict(
        [
            (
                substage,
                list_of_ticksheet_items_for_substage_given_list_of_ticksheet_items_for_qualification(
                    substage=substage,
                    list_of_tick_sheet_items_for_qualification=list_of_tick_sheet_items_for_qualification,
                ),
            )
            for substage in list_of_substages
        ]
    )

    return TickSubStagesAsDict(items_as_dict)


def list_of_substages_given_list_of_tick_sheet_items(
    list_of_tick_sub_stages: ListOfTickSubStages,
    list_of_tick_sheet_items: ListOfTickSheetItems,
) -> ListOfTickSubStages:
    list_of_substage_ids = list_of_tick_sheet_items.list_of_substage_ids()
    return list_of_substages_given_list_of_ids(
        list_of_substage_ids=list_of_substage_ids,
        list_of_tick_sub_stages=list_of_tick_sub_stages,
    )


def list_of_substages_given_list_of_ids(
    list_of_tick_sub_stages: ListOfTickSubStages, list_of_substage_ids: List[str]
) -> ListOfTickSubStages:
    return ListOfTickSubStages(
        [list_of_tick_sub_stages.object_with_id(id) for id in list_of_substage_ids]
    )


def list_of_ticksheet_items_for_substage_given_list_of_ticksheet_items_for_qualification(
    substage: TickSubStage,
    list_of_tick_sheet_items_for_qualification: ListOfTickSheetItems,
) -> ListOfTickSheetItems:
    return list_of_tick_sheet_items_for_qualification.subset_for_substage_id_ignoring_placeholders(
        substage_id=substage.id
    )

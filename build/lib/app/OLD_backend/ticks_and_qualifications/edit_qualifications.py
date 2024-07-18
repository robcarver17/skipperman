from dataclasses import dataclass
from typing import List

from app.objects.qualifications import Qualification

from app.OLD_backend.data.ticksheets import TickSheetsData

from app.data_access.data_layer.data_layer import DataLayer
from app.objects.ticks import QualificationsAndTickItemsAsDict, TickSubStagesAsDict, TickSubStage, TickSheetItem


def get_tick_items_as_dict_for_qualification(
    data_layer: DataLayer, qualification: Qualification
) -> TickSubStagesAsDict:
    qualifications_and_tick_items_as_dict = get_qualifications_and_tick_items_as_dict(
        data_layer
    )

    return qualifications_and_tick_items_as_dict[qualification]

@dataclass
class AutoCorrectForQualificationEdit:
    substage_names: List[str]

def get_suggestions_for_autocorrect(data_layer: DataLayer, qualification: Qualification):
    qualifications_and_tick_items_as_dict = get_qualifications_and_tick_items_as_dict(
        data_layer
    )

    substage_names = get_suggested_list_of_all_substage_names_excluding_existing_in_qualification(
        qualifications_and_tick_items_as_dict=qualifications_and_tick_items_as_dict,
        qualification=qualification
    )

    return AutoCorrectForQualificationEdit(
        substage_names=substage_names
    )

def get_suggested_list_of_all_substage_names_excluding_existing_in_qualification(qualifications_and_tick_items_as_dict: QualificationsAndTickItemsAsDict, qualification: Qualification):
    all_substage_names = qualifications_and_tick_items_as_dict.list_of_substage_names()
    tick_items_as_dict_for_qualification = qualifications_and_tick_items_as_dict[qualification]
    substage_names_this_qualification = tick_items_as_dict_for_qualification.substage_names()

    return in_x_not_in_y(x=all_substage_names, y=substage_names_this_qualification)


from app.objects.utils import in_x_not_in_y

def get_qualifications_and_tick_items_as_dict(
    data_layer: DataLayer,
) -> QualificationsAndTickItemsAsDict:
    tick_sheet_data = TickSheetsData(data_layer)

    return tick_sheet_data.qualifications_and_tick_items_as_dict()

def get_substage_given_id(
    data_layer: DataLayer,
        substage_id
):
    tick_sheet_data = TickSheetsData(data_layer)
    return tick_sheet_data.list_of_substages_given_list_of_ids([substage_id])[0]


def add_new_substage_to_qualification(data_layer: DataLayer, qualification: Qualification, new_substage_name: str):
    ## deal with empties and existing substages
    tick_sheet_data = TickSheetsData(data_layer)
    tick_sheet_data.add_new_substage_to_qualification(qualification=qualification,
                                                      new_substage_name= new_substage_name)


def add_new_ticklistitem_to_qualification(data_layer: DataLayer, qualification: Qualification, substage: TickSubStage, new_tick_list_name: str):
    tick_sheet_data = TickSheetsData(data_layer)
    tick_sheet_data.add_new_ticklistitem_to_qualification(
        qualification=qualification,
        substage=substage,
        new_tick_list_name=new_tick_list_name
    )

def modify_substage_name(data_layer: DataLayer,
                        existing_substage: TickSubStage,
                         qualification: Qualification,
                         new_name: str):

    tick_sheet_data = TickSheetsData(data_layer)
    tick_sheet_data.modify_substage_name(
        existing_substage=existing_substage,
        qualification=qualification,
        new_name=new_name
    )

def modify_ticksheet_item_name(data_layer: DataLayer,
                                              existing_tick_item: TickSheetItem,
                         new_item_name: str):

    tick_sheet_data = TickSheetsData(data_layer)
    tick_sheet_data.modify_ticksheet_item_name(
        existing_tick_item=existing_tick_item,
        new_item_name=new_item_name
    )
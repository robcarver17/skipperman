from app.objects.qualifications import Qualification

from app.OLD_backend.data.ticksheets import TickSheetsData

from app.data_access.store.data_access import DataLayer
from app.objects.substages import TickSubStage, TickSheetItem


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
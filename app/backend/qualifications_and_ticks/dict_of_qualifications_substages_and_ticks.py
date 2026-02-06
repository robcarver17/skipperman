from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.composed.ticks_in_dicts import (
    TickSubStagesAsDict,
    QualificationsAndTickItemsAsDict,
)
from app.objects.qualifications import Qualification
from app.objects.substages import TickSubStage, TickSheetItem


def add_new_ticklistitem_to_substage(
    interface: abstractInterface,
    substage: TickSubStage,
    new_tick_list_name: str,
):
    interface.update(
        interface.object_store.data_api.data_list_of_tick_sheet_items.add_new_ticklistitem_to_qualification,
        substage_id=substage.id,
        new_tick_list_name=new_tick_list_name
    )

def modify_ticksheet_item_name(
    interface: abstractInterface, existing_tick_item: TickSheetItem, new_item_name: str
):

    interface.update(interface.object_store.data_api.data_list_of_tick_sheet_items.modify_ticksheet_item_name,
                     existing_tick_item_id = existing_tick_item.id,
                     new_item_name=new_item_name)


def modify_substage_name(
    interface: abstractInterface,
    existing_substage: TickSubStage,
    new_name: str,
):
    interface.update(
        interface.object_store.data_api.data_list_of_tick_sub_stages.modify_substage_name,
        existing_substage_id=existing_substage.id,
        new_name=new_name
    )



def add_new_substage_to_qualification(
    interface: abstractInterface, qualification: Qualification, new_substage_name: str
):
    interface.update(
        interface.object_store.data_api.data_list_of_tick_sub_stages.add_new_substage_to_qualification,
        qualification_id = qualification.id,
        new_substage_name=new_substage_name
    )


def get_tick_items_as_dict_for_qualification(
    object_store: ObjectStore, qualification: Qualification
) -> TickSubStagesAsDict:
    qualifications_and_tick_items_as_dict = get_qualifications_and_tick_items_as_dict(
        object_store
    )

    return qualifications_and_tick_items_as_dict[qualification]


def get_qualifications_and_tick_items_as_dict(
    object_store: ObjectStore,
) -> QualificationsAndTickItemsAsDict:
    return object_store.get(
        object_store.data_api.data_list_of_tick_sheet_items.get_qualifications_and_tick_items_as_dict
    )



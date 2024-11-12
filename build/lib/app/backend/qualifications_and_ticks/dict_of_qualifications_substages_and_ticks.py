from app.data_access.store.object_definitions import (
    object_definition_for_qualifications_and_tick_items_as_dict,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.composed.ticks_in_dicts import (
    TickSubStagesAsDict,
    QualificationsAndTickItemsAsDict,
)
from app.objects.qualifications import Qualification
from app.objects.substages import TickSubStage, TickSheetItem


def add_new_ticklistitem_to_qualification(
    object_store: ObjectStore,
    qualification: Qualification,
    substage: TickSubStage,
    new_tick_list_name: str,
):
    qualifications_and_tick_items_as_dict = get_qualifications_and_tick_items_as_dict(
        object_store
    )
    qualifications_and_tick_items_as_dict.add_new_ticklistitem_to_qualification(
        qualification=qualification,
        substage=substage,
        new_tick_list_name=new_tick_list_name,
    )
    update_qualifications_and_tick_items_as_dict(
        object_store=object_store,
        qualifications_and_tick_items_as_dict=qualifications_and_tick_items_as_dict,
    )


def modify_substage_name(
    object_store: ObjectStore,
    existing_substage: TickSubStage,
    qualification: Qualification,
    new_name: str,
):
    qualifications_and_tick_items_as_dict = get_qualifications_and_tick_items_as_dict(
        object_store
    )
    qualifications_and_tick_items_as_dict.modify_substage_name(
        existing_substage=existing_substage,
        qualification=qualification,
        new_name=new_name,
    )
    update_qualifications_and_tick_items_as_dict(
        object_store=object_store,
        qualifications_and_tick_items_as_dict=qualifications_and_tick_items_as_dict,
    )


def modify_ticksheet_item_name(
    object_store: ObjectStore, existing_tick_item: TickSheetItem, new_item_name: str
):
    qualifications_and_tick_items_as_dict = get_qualifications_and_tick_items_as_dict(
        object_store
    )
    qualifications_and_tick_items_as_dict.modify_ticksheet_item_name(
        existing_tick_item=existing_tick_item, new_item_name=new_item_name
    )
    update_qualifications_and_tick_items_as_dict(
        object_store=object_store,
        qualifications_and_tick_items_as_dict=qualifications_and_tick_items_as_dict,
    )


def add_new_substage_to_qualification(
    object_store: ObjectStore, qualification: Qualification, new_substage_name: str
):
    ## deal with empties and existing substages
    qualifications_and_tick_items_as_dict = get_qualifications_and_tick_items_as_dict(
        object_store
    )
    qualifications_and_tick_items_as_dict.add_new_substage_to_qualification(
        qualification=qualification, new_substage_name=new_substage_name
    )
    update_qualifications_and_tick_items_as_dict(
        object_store=object_store,
        qualifications_and_tick_items_as_dict=qualifications_and_tick_items_as_dict,
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
    return object_store.get(object_definition_for_qualifications_and_tick_items_as_dict)


def update_qualifications_and_tick_items_as_dict(
    object_store: ObjectStore,
    qualifications_and_tick_items_as_dict: QualificationsAndTickItemsAsDict,
):
    object_store.update(
        new_object=qualifications_and_tick_items_as_dict,
        object_definition=object_definition_for_qualifications_and_tick_items_as_dict,
    )

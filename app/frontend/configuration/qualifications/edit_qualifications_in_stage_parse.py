from app.backend.qualifications_and_ticks.list_of_substages import get_substage_given_id
from app.backend.qualifications_and_ticks.dict_of_qualifications_substages_and_ticks import (
    get_tick_items_as_dict_for_qualification,
    add_new_substage_to_qualification,
    add_new_ticklistitem_to_qualification,
    modify_substage_name,
    modify_ticksheet_item_name,
)

from app.frontend.shared.qualification_and_tick_state_storage import (
    get_qualification_from_state,
)

from app.objects.qualifications import Qualification

from app.frontend.configuration.qualifications.edit_qualifications_in_detail_form import (
    FIELDNAME_FOR_NEW_SUBSTAGE_TEXT_BOX,
    substage_id_for_button_name_new_item,
    fieldname_for_new_item_in_substage_name,
    name_of_edit_substage_field,
    name_of_edit_tickitem_field,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.substages import TickSubStage, TickSheetItem, ListOfTickSheetItems
from app.objects.composed.ticks_in_dicts import TickSubStagesAsDict
from app.objects.utilities.exceptions import MISSING_FROM_FORM


def add_new_substage_to_qualification_from_form(interface: abstractInterface):
    qualification = get_qualification_from_state(interface)
    new_substage_name = interface.value_from_form(FIELDNAME_FOR_NEW_SUBSTAGE_TEXT_BOX, default=MISSING_FROM_FORM)

    try:
        if new_substage_name is MISSING_FROM_FORM:
            raise "Form missing new name entry for %s" % qualification.name
        add_new_substage_to_qualification(
            object_store=interface.object_store,
            qualification=qualification,
            new_substage_name=new_substage_name,
        )
    except Exception as e:
        interface.log_error(
            "Can't add new substage %s because error %s" % (new_substage_name, str(e))
        )


def add_new_tick_list_item_from_form(interface: abstractInterface, button_pressed: str):
    qualification = get_qualification_from_state(interface)

    substage_id = substage_id_for_button_name_new_item(button_pressed)
    substage = get_substage_given_id(
        object_store=interface.object_store, substage_id=substage_id
    )

    fieldname = fieldname_for_new_item_in_substage_name(substage)
    new_tick_list_name = interface.value_from_form(fieldname, default=MISSING_FROM_FORM)

    try:
        if new_tick_list_name is MISSING_FROM_FORM:
            raise "Can't add new tick list name for %s %s because form value missing" % (qualification.name, substage)
        add_new_ticklistitem_to_qualification(
            object_store=interface.object_store,
            qualification=qualification,
            substage=substage,
            new_tick_list_name=new_tick_list_name,
        )
    except Exception as e:
        interface.log_error(
            "Can't add new ticklist item %s for stage %s because error %s"
            % (new_tick_list_name, substage.name, str(e))
        )


def save_edited_values_in_qualifications_form(interface: abstractInterface):
    qualification = get_qualification_from_state(interface)
    tick_items_as_dict = get_tick_items_as_dict_for_qualification(
        object_store=interface.object_store, qualification=qualification
    )
    for substage in tick_items_as_dict.keys():
        save_edited_values_in_qualifications_form_for_substage(
            interface=interface,
            tick_items_as_dict=tick_items_as_dict,
            qualification=qualification,
            substage=substage,
        )


def save_edited_values_in_qualifications_form_for_substage(
    interface: abstractInterface,
    tick_items_as_dict: TickSubStagesAsDict,
    qualification: Qualification,
    substage: TickSubStage,
):
    tick_items_for_substage = tick_items_as_dict[substage]

    save_edited_substage_name_in_qualifications_form_for_substage(
        interface=interface, qualification=qualification, substage=substage
    )
    save_edited_ticklist_itemnames_in_qualifications_form_for_substage(
        interface=interface, tick_items_for_substage=tick_items_for_substage
    )


def save_edited_substage_name_in_qualifications_form_for_substage(
    interface: abstractInterface, qualification: Qualification, substage: TickSubStage
):
    field_name = name_of_edit_substage_field(substage=substage)
    edited_name = interface.value_from_form(field_name, default=MISSING_FROM_FORM)

    if edited_name == substage.name:
        return

    try:
        if edited_name is MISSING_FROM_FORM:
            raise "Can't edit substage name for %s %s %s because form value missing" % (qualification.name, substage.name, field_name)
        modify_substage_name(
            object_store=interface.object_store,
            qualification=qualification,
            existing_substage=substage,
            new_name=edited_name,
        )

    except Exception as e:
        interface.log_error(
            "Couldn't modify substage name from %s to %s because of error %s"
            % (substage.name, edited_name, str(e))
        )


def save_edited_ticklist_itemnames_in_qualifications_form_for_substage(
    interface: abstractInterface, tick_items_for_substage: ListOfTickSheetItems
):
    for tick_item in tick_items_for_substage:
        save_edited_ticklist_itemnames_in_qualifications_form_for_tick_item(
            interface=interface, tick_item=tick_item
        )


def save_edited_ticklist_itemnames_in_qualifications_form_for_tick_item(
    interface: abstractInterface, tick_item: TickSheetItem
):
    fieldname = name_of_edit_tickitem_field(tick_item)
    new_item_name = interface.value_from_form(fieldname, default=MISSING_FROM_FORM)

    if new_item_name == tick_item.name:
        return

    try:
        if new_item_name is MISSING_FROM_FORM:
            raise "Field entry name missing"

        modify_ticksheet_item_name(
            object_store=interface.object_store,
            existing_tick_item=tick_item,
            new_item_name=new_item_name,
        )
    except Exception as e:
        interface.log_error("Can't modify ticksheet name for %s because %s" % (fieldname, str(e)))
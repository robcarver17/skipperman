from app.OLD_backend.ticks_and_qualifications.edit_qualifications import get_tick_items_as_dict_for_qualification, \
    get_substage_given_id, add_new_substage_to_qualification, add_new_ticklistitem_to_qualification, \
    modify_substage_name, modify_ticksheet_item_name

from app.frontend.shared.qualification_and_tick_state_storage import get_qualification_from_state

from app.objects_OLD.qualifications import Qualification

from app.frontend.configuration.qualifications.edit_qualifications_in_detail_form import \
    FIELDNAME_FOR_NEW_SUBSTAGE_TEXT_BOX, substage_id_for_button_name_new_item, fieldname_for_new_item_in_substage_name, \
    name_of_edit_substage_field, name_of_edit_tickitem_field
from app.objects_OLD.abstract_objects.abstract_interface import abstractInterface
from app.objects_OLD.ticks import TickSubStage, TickSubStagesAsDict, TickSheetItem, ListOfTickSheetItems


def add_new_substage_to_qualification_from_form(interface: abstractInterface):
    qualification = get_qualification_from_state(interface)
    new_substage_name = interface.value_from_form(FIELDNAME_FOR_NEW_SUBSTAGE_TEXT_BOX)

    try:
        add_new_substage_to_qualification(data_layer=interface.data,
                                          qualification=qualification,
                                          new_substage_name=new_substage_name)
    except Exception as e:
        interface.log_error("Can't add new substage %s because error %s" % (new_substage_name, str(e)))



def add_new_tick_list_item_from_form(interface: abstractInterface, button_pressed: str):
    qualification = get_qualification_from_state(interface)

    substage_id = substage_id_for_button_name_new_item(button_pressed)
    substage = get_substage_given_id(data_layer=interface.data, substage_id=substage_id)

    fieldname = fieldname_for_new_item_in_substage_name(substage)
    new_tick_list_name = interface.value_from_form(fieldname)

    try:
        add_new_ticklistitem_to_qualification(
            data_layer=interface.data,
            qualification=qualification,
            substage=substage,
            new_tick_list_name=new_tick_list_name

        )
    except Exception as e:
        interface.log_error("Can't add new ticklist item %s for stage %s because error %s" % (new_tick_list_name, substage.name, str(e)))

def save_edited_values_in_qualifications_form(interface: abstractInterface):
    qualification = get_qualification_from_state(interface)
    tick_items_as_dict = get_tick_items_as_dict_for_qualification(
        data_layer=interface.data, qualification=qualification
    )
    for substage in tick_items_as_dict.keys():
        save_edited_values_in_qualifications_form_for_substage(interface=interface,
                                                               tick_items_as_dict=tick_items_as_dict,
                                                               qualification=qualification, substage=substage)

def save_edited_values_in_qualifications_form_for_substage(interface: abstractInterface,
                                                           tick_items_as_dict: TickSubStagesAsDict,
                                                           qualification: Qualification, substage: TickSubStage):
    tick_items_for_substage = tick_items_as_dict[substage]

    save_edited_substage_name_in_qualifications_form_for_substage(interface=interface, qualification=qualification, substage=substage)
    save_edited_ticklist_itemnames_in_qualifications_form_for_substage(interface=interface,
                                                                       tick_items_for_substage=tick_items_for_substage)

def save_edited_substage_name_in_qualifications_form_for_substage(interface: abstractInterface, qualification: Qualification, substage: TickSubStage):
    field_name = name_of_edit_substage_field(substage=substage)
    edited_name = interface.value_from_form(field_name)

    if edited_name == substage.name:
        return

    try:
        modify_substage_name(data_layer=interface.data,
                             qualification=qualification,
                             existing_substage=substage,
                             new_name=edited_name)

    except Exception as e:
        interface.log_error("Couldn't modify substage name from %s to %s because of error %s" % (substage.name, edited_name, str(e)))



def save_edited_ticklist_itemnames_in_qualifications_form_for_substage(interface: abstractInterface,
                                                                       tick_items_for_substage: ListOfTickSheetItems):

    for tick_item in tick_items_for_substage:
        save_edited_ticklist_itemnames_in_qualifications_form_for_tick_item(
            interface=interface, tick_item=tick_item
        )

def save_edited_ticklist_itemnames_in_qualifications_form_for_tick_item(interface: abstractInterface,

                                                                       tick_item: TickSheetItem):
    fieldname = name_of_edit_tickitem_field(tick_item)
    new_item_name = interface.value_from_form(fieldname)

    if new_item_name == tick_item.name:
        return

    modify_ticksheet_item_name(data_layer=interface.data, existing_tick_item=tick_item, new_item_name=new_item_name)





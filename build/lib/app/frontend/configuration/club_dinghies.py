from typing import Union, List

from app.backend.club_boats.club_boat_limits import get_dict_of_club_dinghy_limits, clear_and_set_generic_limit
from app.data_access.store.object_store import ObjectStore

from app.backend.club_boats.list_of_club_dinghies import (
    update_list_of_club_dinghies,
    add_new_club_dinghy_given_string,
    modify_club_dinghy,
)

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.configuration.generic_list_modifier import (
    display_form_edit_generic_list,
    post_form_edit_generic_list,
    BACK_BUTTON_PRESSED,
    BUTTON_NOT_KNOWN, hide_button_for_entry, up_button_for_entry, down_button_for_entry, hidden_box_name,
)
from app.frontend.forms.form_utils import is_radio_yes_or_no
from app.objects.abstract_objects.abstract_form import Form, NewForm, textInput, intInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.abstract_objects.abstract_tables import RowInTable
from app.objects.club_dinghies import ClubDinghy, ListOfClubDinghies
from app.objects.composed.club_dinghy_limits import ClubDinghyAndGenericLimit
from app.objects.exceptions import arg_not_passed

header_text = "List of club dinghies: add, edit or re-order"


def display_form_config_club_dinghies_page(interface: abstractInterface) -> Form:
    list_of_boats_and_limits = get_list_of_boats_and_limits(object_store=interface.object_store)
    return display_form_edit_generic_list(
        existing_list=list_of_boats_and_limits,
        header_text=header_text,
        function_for_existing_entry_row=get_row_for_existing_entry
    )

def get_list_of_boats_and_limits(object_store: ObjectStore) -> List[ClubDinghyAndGenericLimit]:
    dict_of_limits = get_dict_of_club_dinghy_limits(object_store)
    list_of_boats_and_limits = dict_of_limits.list_of_generic_limits_for_all_boats()

    return list_of_boats_and_limits

def get_row_for_existing_entry(entry: ClubDinghyAndGenericLimit, **ignored_kwargs) -> RowInTable:
    return RowInTable(
        [            text_box_for_dinghy(entry),
                     get_input_cell_for_boat_limits(entry),
                     hide_button_for_entry(entry),
                     Line([up_button_for_entry(entry), down_button_for_entry(entry)]),
                     ])

def text_box_for_dinghy(entry: ClubDinghyAndGenericLimit = arg_not_passed) -> textInput:
    if entry is arg_not_passed:
        entry_value = ""
        input_label = "Add new entry"
    else:
        entry_value = entry.club_dinghy.name
        input_label = "Edit"

    return textInput(
        input_label=input_label,
        input_name=name_of_text_box_for_boat(entry),
        value=entry_value,
    )

BOAT_NAME = "boatname"
NEW_BOAT_NAME = "newboat"
def name_of_text_box_for_boat(entry: ClubDinghyAndGenericLimit = arg_not_passed) -> str:
    if entry is arg_not_passed:
        return NEW_BOAT_NAME
    else:
        return BOAT_NAME + "_" + entry.club_dinghy.id

def get_input_cell_for_boat_limits(entry: ClubDinghyAndGenericLimit) -> intInput:
    return intInput(input_name=get_cell_name_for_boat_limits(entry),
                    input_label='Number available',
                    value = int(entry.limit))

BOAT_LIMIT_INPUT = "Boatlimitinput"
def get_cell_name_for_boat_limits(entry: ClubDinghyAndGenericLimit):
    return BOAT_LIMIT_INPUT+"^"+entry.club_dinghy.id


def post_form_config_club_dinghies_page(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    list_of_boats_and_limits  =get_list_of_boats_and_limits(object_store=interface.object_store)

    generic_list_output = post_form_edit_generic_list(
        existing_list=list_of_boats_and_limits,
        interface=interface,
        header_text=header_text,
        adding_function=add_new_club_dinghy_given_string,
        modifying_function=modify_club_dinghy_and_limit,
        save_function=save_from_ordinary_list_of_club_dinghies_and_limits,
        get_object_from_form_function=get_modified_dinghy_and_limit_from_form,
    )

    if generic_list_output is BACK_BUTTON_PRESSED:
        interface.clear_cache()
        return interface.get_new_display_form_for_parent_of_function(
            post_form_config_club_dinghies_page
        )
    elif generic_list_output is BUTTON_NOT_KNOWN:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()

    return interface.get_new_form_given_function(display_form_config_club_dinghies_page)




def get_modified_dinghy_and_limit_from_form(
    interface: abstractInterface, existing_object: ClubDinghyAndGenericLimit, **ignored_kwargs
) -> ClubDinghyAndGenericLimit:
    existing_dinghy_and_limit = existing_object

    new_dinghy_name = interface.value_from_form(name_of_text_box_for_boat(existing_dinghy_and_limit))
    new_limit = interface.value_from_form(get_cell_name_for_boat_limits(existing_dinghy_and_limit))

    new_hidden = is_radio_yes_or_no(
        interface=interface, input_name=hidden_box_name(existing_dinghy_and_limit)
    )

    modified_boat_and_limits = ClubDinghyAndGenericLimit(
        club_dinghy=ClubDinghy(name=new_dinghy_name, hidden=new_hidden),
        limit=new_limit,
        hidden=new_hidden
    )

    return modified_boat_and_limits

def modify_club_dinghy_and_limit(
    object_store: ObjectStore, existing_object: ClubDinghyAndGenericLimit, new_object: ClubDinghyAndGenericLimit
):
    modify_club_dinghy(object_store=object_store, existing_object=existing_object.club_dinghy, new_object=new_object.club_dinghy)
    clear_and_set_generic_limit(object_store=object_store, original_boat=existing_object.club_dinghy, new_boat=new_object.club_dinghy, new_limit=new_object.limit)

def save_from_ordinary_list_of_club_dinghies_and_limits(
    object_store: ObjectStore, new_list: List[ClubDinghyAndGenericLimit]
):
    ## We don't need to do the limits as order doesn't matter - changes to limits will be done in modify
    list_of_club_dinghies = [item.club_dinghy for item in new_list]
    update_list_of_club_dinghies(
        object_store=object_store,
        updated_list_of_club_dinghies=ListOfClubDinghies(list_of_club_dinghies),
    )


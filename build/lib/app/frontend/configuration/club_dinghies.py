from typing import Union, List

from app.data_access.store.object_store import ObjectStore

from app.backend.club_boats.list_of_club_dinghies import get_list_of_boat_classes, update_list_of_boat_classes, \
    add_new_club_dinghy_given_string,  \
    modify_club_dinghy

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.configuration.generic_list_modifier import (
    display_form_edit_generic_list,
    post_form_edit_generic_list,
    BACK_BUTTON_PRESSED,
    BUTTON_NOT_KNOWN,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.club_dinghies import ClubDinghy, ListOfClubDinghies

header_text = "List of club dinghies: add, edit or re-order"


def display_form_config_club_dinghies_page(interface: abstractInterface) -> Form:
    list_of_boats = get_list_of_boat_classes(interface.object_store)

    return display_form_edit_generic_list(
        existing_list=list_of_boats,
        header_text=header_text,
    )


def post_form_config_club_dinghies_page(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    list_of_boats = get_list_of_boat_classes(interface.object_store)

    generic_list_output = post_form_edit_generic_list(
        existing_list=list_of_boats,
        interface=interface,
        header_text=header_text,
        adding_function=add_new_club_dinghy_given_string,
        modifying_function=modify_club_dinghy,
        save_function=save_from_ordinary_list_of_club_dinghies,
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

def save_from_ordinary_list_of_club_dinghies(
    object_store: ObjectStore, new_list: List[ClubDinghy]
):
    update_list_of_boat_classes(object_store=object_store, updated_list_of_boat_classes=ListOfClubDinghies(new_list))
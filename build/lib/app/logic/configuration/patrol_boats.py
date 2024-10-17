from typing import Union, List

from app.OLD_backend.configuration import (
    save_list_of_patrol_boats,
    load_list_of_patrol_boats,
)
from app.backend.patrol_boats.list_of_patrol_boats import add_new_patrol_boat, \
    delete_patrol_boat_given_string, modify_patrol_boat

from app.frontend.form_handler import (
    button_error_and_back_to_initial_state_form,
)
from app.frontend.configuration.generic_list_modifier import (
    display_form_edit_generic_list,
    post_form_edit_generic_list,
    BACK_BUTTON_PRESSED,
    BUTTON_NOT_KNOWN,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.patrol_boats import PatrolBoat, ListOfPatrolBoats

header_text = "List of club patrol boats: add, edit, or re-order"


def display_form_config_patrol_boats_page(interface: abstractInterface) -> Form:
    list_of_boats = load_list_of_patrol_boats(interface)

    return display_form_edit_generic_list(
        existing_list=list_of_boats,
        header_text=header_text,
    )


def post_form_config_patrol_boats_page(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    list_of_boats = load_list_of_patrol_boats(interface)

    generic_list_output = post_form_edit_generic_list(
        existing_list=list_of_boats,
        interface=interface,
        header_text=header_text,
        deleting_function=delete_patrol_boat_given_string,
        adding_function=add_new_patrol_boat,
        modifying_function=modify_patrol_boat,
        save_function=save_from_ordinary_list_of_patrol_boats,
    )
    if generic_list_output is BACK_BUTTON_PRESSED:
        return interface.get_new_display_form_for_parent_of_function(
            post_form_config_patrol_boats_page
        )
    elif generic_list_output is BUTTON_NOT_KNOWN:
        return button_error_and_back_to_initial_state_form(interface)

    return display_form_config_patrol_boats_page(interface)

def save_from_ordinary_list_of_patrol_boats(
    interface: abstractInterface, new_list: List[PatrolBoat]
):
    save_list_of_patrol_boats(
        interface=interface, list_of_boats=ListOfPatrolBoats(new_list)
    )

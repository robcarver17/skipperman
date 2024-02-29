from typing import Union

from app.backend.data.resources import get_list_of_club_dinghies, add_new_club_dinghy_given_string_and_return_list, modify_club_dinghy_given_string_and_return_list, delete_club_dinghy_given_string_and_return_list

from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.configuration.generic_list_modifier import display_form_edit_generic_list, post_form_edit_generic_list, BACK_BUTTON_PRESSED, BUTTON_NOT_KNOWN
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_interface import abstractInterface

header_text = ListOfLines(["List of club dinghies: add, edit or delete"])




def display_form_config_club_dinghies_page(interface: abstractInterface) -> Form:
    list_of_boats = get_list_of_club_dinghies()

    return display_form_edit_generic_list(
        existing_list=list_of_boats,
        header_text=header_text,
    )



def post_form_config_club_dinghies_page(interface: abstractInterface) -> Union[Form, NewForm]:
    list_of_boats = get_list_of_club_dinghies()

    generic_list_output = post_form_edit_generic_list(
        existing_list=list_of_boats,
        interface=interface,
        header_text=header_text,
        deleting_function=delete_club_dinghy_given_string_and_return_list,
        adding_function=add_new_club_dinghy_given_string_and_return_list,
        modifying_function=modify_club_dinghy_given_string_and_return_list,
        re_order_function=re_order_club_dinghy_and_return_list
    )
    if generic_list_output is BACK_BUTTON_PRESSED:
        return interface.get_new_display_form_for_parent_of_function(post_form_config_club_dinghies_page)
    elif generic_list_output is BUTTON_NOT_KNOWN:
        return button_error_and_back_to_initial_state_form(interface)
    else:
        return generic_list_output

def re_order_club_dinghy_and_return_list(direction: str, selected_entry_name:str):
    pass
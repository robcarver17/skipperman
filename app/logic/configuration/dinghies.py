from typing import Union, List

from app.backend.data.resources import load_list_of_boat_classes, modify_boat_class_given_string_and_return_list, delete_boat_class_given_string_and_return_list, add_new_boat_class_given_string_and_return_list, save_list_of_boat_classes

from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.configuration.generic_list_modifier import display_form_edit_generic_list, post_form_edit_generic_list, BACK_BUTTON_PRESSED, BUTTON_NOT_KNOWN
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.dinghies import Dinghy, ListOfDinghies

header_text = ListOfLines(["List of boat classes: add, edit or delete; re-order"])



def display_form_config_boat_classes_page(interface: abstractInterface) -> Form:
    list_of_boats = load_list_of_boat_classes()

    return display_form_edit_generic_list(
        existing_list=list_of_boats,
        header_text=header_text,
    )



def post_form_config_dinghies_page(interface: abstractInterface) -> Union[Form, NewForm]:
    list_of_boats = load_list_of_boat_classes()

    generic_list_output = post_form_edit_generic_list(
        existing_list=list_of_boats,
        interface=interface,
        header_text=header_text,
        deleting_function=delete_boat_class_given_string_and_return_list,
        adding_function=add_new_boat_class_given_string_and_return_list,
        modifying_function=modify_boat_class_given_string_and_return_list,
        save_function=save_from_ordinary_list_of_dinghies
    )
    if generic_list_output is BACK_BUTTON_PRESSED:
        return interface.get_new_display_form_for_parent_of_function(post_form_config_dinghies_page)
    elif generic_list_output is BUTTON_NOT_KNOWN:
        return button_error_and_back_to_initial_state_form(interface)
    else:
        return generic_list_output

def save_from_ordinary_list_of_dinghies(list_of_dinghies: List[Dinghy]):
    save_list_of_boat_classes(ListOfDinghies(list_of_dinghies))

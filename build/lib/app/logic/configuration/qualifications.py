from typing import Union, List

from app.backend.data.qualification import DEPRECATE_load_list_of_qualifications, DEPRECATE_save_list_of_qualifications
from app.backend.ticks_and_qualifications.qualifications import add_new_qualification_given_string_and_return_list, \
    delete_qualification_given_string_and_return_list, modify_qualification_given_string_and_return_list

from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.configuration.generic_list_modifier import display_form_edit_generic_list, post_form_edit_generic_list, BACK_BUTTON_PRESSED, BUTTON_NOT_KNOWN
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.qualifications import Qualification, ListOfQualifications

header_text = "List of qualifications: add, edit, re-order"



def display_form_config_qualifications_page(interface: abstractInterface) -> Form:
    list_of_qualifications = DEPRECATE_load_list_of_qualifications()

    return display_form_edit_generic_list(
        existing_list=list_of_qualifications,
        header_text=header_text,
    )



def post_form_config_qualifications_page(interface: abstractInterface) -> Union[Form, NewForm]:
    list_of_qualifications = DEPRECATE_load_list_of_qualifications()

    generic_list_output = post_form_edit_generic_list(
        existing_list=list_of_qualifications,
        interface=interface,
        header_text=header_text,
        deleting_function=delete_qualification_given_string_and_return_list,
        adding_function=add_new_qualification_given_string_and_return_list,
        modifying_function=modify_qualification_given_string_and_return_list,
        save_function=save_from_ordinary_list_of_qualifications
    )
    if generic_list_output is BACK_BUTTON_PRESSED:
        return interface.get_new_display_form_for_parent_of_function(post_form_config_qualifications_page)
    elif generic_list_output is BUTTON_NOT_KNOWN:
        return button_error_and_back_to_initial_state_form(interface)
    else:
        return generic_list_output

def save_from_ordinary_list_of_qualifications(list_of_qualifications: List[Qualification]):
    DEPRECATE_save_list_of_qualifications(ListOfQualifications(list_of_qualifications))

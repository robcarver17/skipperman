from typing import Union

from app.logic.abstract_logic_api import initial_state_form
from app.logic.utilities.data_and_backups.data_and_backups import display_form_data_and_backups

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import main_menu_button, Button
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.constants import missing_data

DATA_AND_BACKUP = "Data: backup, upload, and restore"

## MODIFY THIS TO ADD MORE REPORTS
DICT_OF_MENU_OPTIONS ={
    DATA_AND_BACKUP: display_form_data_and_backups
}

list_of_menu_labels=list(DICT_OF_MENU_OPTIONS.keys())
list_of_menu_buttons = ListOfLines([Button(label) for label in list_of_menu_labels])

def function_given_pressed_button_label(label) -> str:
    return DICT_OF_MENU_OPTIONS.get(label, missing_data)

def display_form_utilities_menu(interface: abstractInterface) -> Form:
    lines_inside_form = ListOfLines(
        [
            main_menu_button,
            _______________,
            "Select option:",
            _______________]+
            list_of_menu_buttons
    )

    return Form(lines_inside_form)


def post_form_utilities_menu(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    utility_function = function_given_pressed_button_label(button_pressed)
    if utility_function is missing_data:
        interface.log_error("Options %s missing from dict contact support" % button_pressed)
        return initial_state_form

    return interface.get_new_form_given_function(utility_function)

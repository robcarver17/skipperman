from typing import Union

from app.frontend.form_handler import initial_state_form
from app.frontend.utilities.cleaning.ENTRY_cleaning import display_form_for_event_cleaning
from app.frontend.utilities.data_and_backups.ENTRY_data_and_backups import (
    display_form_data_and_backups,
)
from app.frontend.utilities.files.ENTRY_files import display_form_file_management

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import (
    main_menu_button,
    Button,
    ButtonBar,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    Line,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.exceptions import missing_data

DATA_AND_BACKUP = "Data: backup, upload, and restore"
DATA_CLEAN = "Delete sensitive data"
FILES = "File management"

## MODIFY THIS TO ADD MORE REPORTS
DICT_OF_MENU_OPTIONS = {
    DATA_AND_BACKUP: display_form_data_and_backups,
    DATA_CLEAN: display_form_for_event_cleaning,
    FILES: display_form_file_management,
}

list_of_menu_labels = list(DICT_OF_MENU_OPTIONS.keys())
list_of_menu_buttons = Line([Button(label, tile=True) for label in list_of_menu_labels])

nav_buttons = ButtonBar([main_menu_button])


def function_given_pressed_button_label(label) -> str:
    return DICT_OF_MENU_OPTIONS.get(label, missing_data)


def display_form_utilities_menu(interface: abstractInterface) -> Form:
    lines_inside_form = ListOfLines([nav_buttons, list_of_menu_buttons])

    return Form(lines_inside_form)


def post_form_utilities_menu(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    utility_function = function_given_pressed_button_label(button_pressed)
    if utility_function is missing_data:
        interface.log_error(
            "Options %s missing from dict contact support" % button_pressed
        )
        return initial_state_form

    return interface.get_new_form_given_function(utility_function)

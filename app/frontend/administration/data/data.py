from typing import Union

from app.objects.abstract_objects.abstract_text import Heading

from app.data_access.backups.find_and_restore_backups import delete_all_master_data
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines

from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    Button,
    back_menu_button,
)

from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface

DELETE_ALL_DATA_BUTTON_LABEL = "Delete all data"
delete_all_data_button = Button(DELETE_ALL_DATA_BUTTON_LABEL, tile=True)
nav_buttons = ButtonBar([back_menu_button])
config_option_buttons = Line([delete_all_data_button])


def display_form_data(interface: abstractInterface) -> Union[Form, NewForm]:
    warning = Heading(
        "Deleting data cannot be undone. There will be no 'are you sure'. DO NOT PRESS UNLESS REALLY SURE!",
        size=1,
        centred=True,
    )
    lines_inside_form = ListOfLines([nav_buttons, warning, config_option_buttons])

    return Form(lines_inside_form)


def post_form_data(interface: abstractInterface) -> Union[Form, NewForm]:
    last_button = interface.last_button_pressed()
    if back_menu_button.pressed(last_button):
        return interface.get_new_display_form_for_parent_of_function(post_form_data)

    if delete_all_data_button.pressed(last_button):
        delete_all_master_data(interface, are_you_sure=True)
        interface.log_error("Deleted all data except users/passwords")
        return interface.get_new_form_given_function(display_form_data)
    else:
        return button_error_and_back_to_initial_state_form(interface)

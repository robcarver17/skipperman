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

nav_buttons = ButtonBar([back_menu_button])

def display_form_data(interface: abstractInterface) -> Union[Form, NewForm]:
    warning = Heading(
        "No options available here - can no longer delete data via web interface",
        size=1,
        centred=True,
    )
    lines_inside_form = ListOfLines([nav_buttons, warning])

    return Form(lines_inside_form)


def post_form_data(interface: abstractInterface) -> Union[Form, NewForm]:
    last_button = interface.last_button_pressed()
    if back_menu_button.pressed(last_button):
        return interface.get_new_display_form_for_parent_of_function(post_form_data)
    else:
        return button_error_and_back_to_initial_state_form(interface)

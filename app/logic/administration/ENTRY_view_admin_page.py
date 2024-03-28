from typing import Union

from app.logic.administration.users import display_form_security
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm, )
from app.objects.abstract_objects.abstract_buttons import main_menu_button, Button, ButtonBar
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.abstract_objects.abstract_interface import abstractInterface

USERS_BUTTON_LABEL = "Users, passwords and access"

nav_buttons = ButtonBar([main_menu_button])
config_option_buttons = Line([Button(USERS_BUTTON_LABEL, tile=True)])

def display_form_main_admin_page(interface: abstractInterface) -> Form:
    lines_inside_form = ListOfLines(
        [
            nav_buttons,
            config_option_buttons
        ]
    )

    return Form(lines_inside_form)


def post_form_main_admin_page(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed==USERS_BUTTON_LABEL:
        return interface.get_new_form_given_function(display_form_security)



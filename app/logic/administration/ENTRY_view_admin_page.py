from typing import Union

from app.logic.administration.users import display_form_security
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm, )
from app.objects.abstract_objects.abstract_buttons import main_menu_button, Button
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.abstract_objects.abstract_interface import abstractInterface

USERS_BUTTON_LABEL = "Users, passwords and access"

def display_form_main_admin_page(interface: abstractInterface) -> Form:
    lines_inside_form = ListOfLines(
        [
            Button(USERS_BUTTON_LABEL),
            main_menu_button,
        ]
    )

    return Form(lines_inside_form)


def post_form_main_admin_page(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed==USERS_BUTTON_LABEL:
        return interface.get_new_form_given_function(display_form_security)



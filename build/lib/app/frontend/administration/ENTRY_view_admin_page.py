from typing import Union

from app.frontend.administration.data.data import display_form_data
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.administration.users.ENTRY_users import display_form_security
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import (
    main_menu_button,
    Button,
    ButtonBar,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.abstract_objects.abstract_interface import abstractInterface

USERS_BUTTON_LABEL = "Users, passwords and access"
DATA_BUTTON_LABEL = "Data"

user_button = Button(USERS_BUTTON_LABEL, tile=True)
data_button = Button(DATA_BUTTON_LABEL, tile=True)

nav_buttons = ButtonBar([main_menu_button])
config_option_buttons = Line([user_button, data_button])


def display_form_main_admin_page(interface: abstractInterface) -> Form:
    lines_inside_form = ListOfLines([nav_buttons, config_option_buttons])

    return Form(lines_inside_form)


def post_form_main_admin_page(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if user_button.pressed(button_pressed):
        return interface.get_new_form_given_function(display_form_security)
    elif data_button.pressed(button_pressed):
        return interface.get_new_form_given_function(display_form_data)
    else:
        return button_error_and_back_to_initial_state_form(interface)

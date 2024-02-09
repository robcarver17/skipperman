from typing import Union

from app.logic.abstract_logic_api import initial_state_form, button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import main_menu_button, Button
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.configuration.constants import *

CLUB_DINGHIES_BUTTON_LABEL = "Club dinghies"
PATROL_BOATS_BUTTON_LABEL = "Patrol boats"

def display_form_main_config_page(interface: abstractInterface) -> Form:
    lines_inside_form = ListOfLines(
        [
            main_menu_button,
            "Select options to modify",
            _______________,
            Button(CLUB_DINGHIES_BUTTON_LABEL),
            Button(PATROL_BOATS_BUTTON_LABEL)
        ]
    )

    return Form(lines_inside_form)


def post_form_main_config_page(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed == CLUB_DINGHIES_BUTTON_LABEL:
        return NewForm(VIEW_CLUB_DINGHIES_STAGE)

    if button_pressed == PATROL_BOATS_BUTTON_LABEL:
        return NewForm(PATROL_BOATS_BUTTON_LABEL)
    else:
        return button_error_and_back_to_initial_state_form()

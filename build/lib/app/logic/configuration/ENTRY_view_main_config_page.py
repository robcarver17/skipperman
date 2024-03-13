from typing import Union

from app.logic.abstract_logic_api import initial_state_form, button_error_and_back_to_initial_state_form
from app.logic.configuration.club_dinghies import display_form_config_club_dinghies_page
from app.logic.configuration.patrol_boats import display_form_config_patrol_boats_page
from app.logic.configuration.dinghies import display_form_config_boat_classes_page
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import main_menu_button, Button
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_interface import abstractInterface


CLUB_DINGHIES_BUTTON_LABEL = "Club dinghies"
PATROL_BOATS_BUTTON_LABEL = "Patrol boats"
BOAT_CLASSES_BUTTON_LABEL = "Boat classes"

def display_form_main_config_page(interface: abstractInterface) -> Form:
    lines_inside_form = ListOfLines(
        [
            main_menu_button,
            "Select options to modify",
            _______________,
            Button(CLUB_DINGHIES_BUTTON_LABEL),
            Button(PATROL_BOATS_BUTTON_LABEL),
            Button(BOAT_CLASSES_BUTTON_LABEL)
        ]
    )

    return Form(lines_inside_form)


def post_form_main_config_page(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed == CLUB_DINGHIES_BUTTON_LABEL:
        return interface.get_new_form_given_function(display_form_config_club_dinghies_page)

    elif button_pressed == PATROL_BOATS_BUTTON_LABEL:
        return interface.get_new_form_given_function(display_form_config_patrol_boats_page)

    elif button_pressed == BOAT_CLASSES_BUTTON_LABEL:
        return interface.get_new_form_given_function(display_form_config_boat_classes_page)

    else:
        return button_error_and_back_to_initial_state_form(interface)

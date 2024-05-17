from typing import Union

from app.logic.abstract_logic_api import  button_error_and_back_to_initial_state_form
from app.logic.configuration.club_dinghies import display_form_config_club_dinghies_page
from app.logic.configuration.patrol_boats import display_form_config_patrol_boats_page
from app.logic.configuration.boat_classes import display_form_config_boat_classes_page
from app.logic.configuration.qualifications import display_form_config_qualifications_page
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import main_menu_button, Button, ButtonBar
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________, Line
from app.objects.abstract_objects.abstract_interface import abstractInterface


CLUB_DINGHIES_BUTTON_LABEL = "Club dinghies"
PATROL_BOATS_BUTTON_LABEL = "Patrol boats"
BOAT_CLASSES_BUTTON_LABEL = "Boat classes"
QUALIFICATIONS_BUTTON_LABEL = "Qualifications"

dict_of_options_and_functions = {CLUB_DINGHIES_BUTTON_LABEL: display_form_config_club_dinghies_page,
                                 PATROL_BOATS_BUTTON_LABEL: display_form_config_patrol_boats_page,
                                 BOAT_CLASSES_BUTTON_LABEL: display_form_config_boat_classes_page,
                                 QUALIFICATIONS_BUTTON_LABEL: display_form_config_qualifications_page}

all_options = list(dict_of_options_and_functions.keys())

nav_buttons = ButtonBar([main_menu_button])
config_option_buttons = Line([Button(label, tile=True) for label in all_options])

def display_form_main_config_page(interface: abstractInterface) -> Form:
    lines_inside_form = ListOfLines(
        [
            nav_buttons,
            config_option_buttons
        ]
    )

    return Form(lines_inside_form)


def post_form_main_config_page(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed in all_options:
        relevant_function = dict_of_options_and_functions[button_pressed]
        return interface.get_new_form_given_function(relevant_function)
    else:
        return button_error_and_back_to_initial_state_form(interface)

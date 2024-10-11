from typing import Union

from app.frontend.configuration.sailing_groups import display_form_config_sailing_groups
from app.frontend.configuration.teams_and_roles.volunteer_roles import display_form_config_volunteer_roles
from app.frontend.configuration.volunteer_skills import display_form_config_volunteer_skills
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.configuration.club_dinghies import display_form_config_club_dinghies_page
from app.frontend.configuration.patrol_boats import display_form_config_patrol_boats_page
from app.frontend.configuration.boat_classes import display_form_config_boat_classes_page
from app.frontend.configuration.teams_and_roles.volunteer_teams import display_form_config_teams_page
from app.frontend.configuration.qualifications.qualifications import (
    display_form_config_qualifications_page,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import (
    main_menu_button,
    Button,
    ButtonBar, HelpButton,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    Line,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface


CLUB_DINGHIES_BUTTON_LABEL = "Club dinghies"
PATROL_BOATS_BUTTON_LABEL = "Patrol boats"
BOAT_CLASSES_BUTTON_LABEL = "Boat classes"
QUALIFICATIONS_BUTTON_LABEL = "Sailing qualifications"
SAILING_GROUPS = "Sailing groups"
VOLUNTEER_SKILLS = "Volunteer skills"
VOLUNTEER_ROLES = "Volunteer roles"
VOLUNTEER_TEAMS = "Volunteer teams"

dict_of_options_and_functions = {
    CLUB_DINGHIES_BUTTON_LABEL: display_form_config_club_dinghies_page,
    PATROL_BOATS_BUTTON_LABEL: display_form_config_patrol_boats_page,
    BOAT_CLASSES_BUTTON_LABEL: display_form_config_boat_classes_page,
    VOLUNTEER_ROLES: display_form_config_volunteer_roles,
    VOLUNTEER_TEAMS: display_form_config_teams_page,
    VOLUNTEER_SKILLS: display_form_config_volunteer_skills,
    SAILING_GROUPS: display_form_config_sailing_groups,
    QUALIFICATIONS_BUTTON_LABEL: display_form_config_qualifications_page
}

all_options = list(dict_of_options_and_functions.keys())

config_option_buttons = Line([Button(label, tile=True) for label in all_options])


def display_form_main_config_page(interface: abstractInterface) -> Form:
    lines_inside_form = ListOfLines([nav_buttons, config_option_buttons])

    return Form(lines_inside_form)


def post_form_main_config_page(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed in all_options:
        relevant_function = dict_of_options_and_functions[button_pressed]
        return interface.get_new_form_given_function(relevant_function)
    else:
        return button_error_and_back_to_initial_state_form(interface)

help_button = HelpButton("configuration_help")
nav_buttons = ButtonBar([main_menu_button, help_button])

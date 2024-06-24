from typing import Union

from app.backend.volunteers.volunteer_rota_data import get_all_roles_across_recent_events_for_volunteer_id_as_dict
from app.logic.volunteers.delete_volunteer import display_form_delete_individual_volunteer
from app.logic.volunteers.edit_cadet_connections import display_form_edit_cadet_volunteer_connections
from app.logic.volunteers.edit_volunteer import display_form_edit_individual_volunteer
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import Button, ButtonBar, back_menu_button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.abstract_logic_api import initial_state_form, button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.backend.volunteers.volunteers import get_connected_cadets, get_dict_of_existing_skills
from app.logic.volunteers.volunteer_state import get_volunteer_from_state
from app.logic.volunteers.constants import *

from app.objects.volunteers import Volunteer
from app.objects.events import SORT_BY_START_DSC


def display_form_view_individual_volunteer(
    interface: abstractInterface,
) -> Union[Form, NewForm]:

    try:
        volunteer = get_volunteer_from_state(interface)
    except:
        interface.log_error(
            "Volunteer selected no longer in list- someone else has deleted or file corruption?"
        )
        return initial_state_form

    return display_form_for_selected_volunteer(
        volunteer=volunteer, interface=interface
    )




def display_form_for_selected_volunteer(
    volunteer: Volunteer, interface: abstractInterface
) -> Form:
    lines_of_allocations = list_of_lines_with_allocations_and_roles(interface=interface, volunteer=volunteer)

    connected = lines_for_connected_cadets(interface=interface, volunteer=volunteer)
    skills = list_of_skills_as_list_of_lines(interface=interface, volunteer=volunteer)
    buttons = buttons_for_volunteer_form()
    return Form(
        ListOfLines([
            str(volunteer),
            _______________,
            lines_of_allocations,
            _______________,
            skills,
            _______________,
            connected,
            _______________,
            buttons
        ])
    )

def list_of_lines_with_allocations_and_roles(interface: abstractInterface, volunteer: Volunteer) -> ListOfLines:
    dict_of_roles =get_all_roles_across_recent_events_for_volunteer_id_as_dict(
        interface=interface, volunteer_id=volunteer.id,
                                                      sort_by=SORT_BY_START_DSC)
    if len(dict_of_roles)==0:
        return ListOfLines([])

    return ListOfLines(["Events helping at:", _______________]+
        ["%s: %s" % (str(event), role) for event, role in dict_of_roles.items()]
    ).add_Lines()


def list_of_skills_as_list_of_lines(interface: abstractInterface, volunteer: Volunteer) -> ListOfLines:
    skills = get_dict_of_existing_skills(interface=interface, volunteer=volunteer)
    skills_held = [skill for skill, skill_held in skills.items() if skill_held]
    skills_not_held = [skill for skill, skill_held in skills.items() if not skill_held]

    return ListOfLines([
        Line("Skills held: %s" % ", ".join(skills_held)),
        Line("Skills missing: %s" % ", ".join(skills_not_held)),
    ])



def lines_for_connected_cadets(interface: abstractInterface, volunteer: Volunteer) -> Line:
    cadets = get_connected_cadets(interface=interface, volunteer=volunteer)
    cadets_as_str = [str(cadet) for cadet in cadets]
    if len(cadets)==0:
        return Line([])
    return Line(
        "Connected to: %s" % ", ".join(cadets_as_str)
    )

def buttons_for_volunteer_form() -> ButtonBar:
    return ButtonBar([back_menu_button, Button(EDIT_BUTTON_LABEL, nav_button=True),  Button(EDIT_CADET_CONNECTIONS_BUTTON_LABEL, nav_button=True)])


def post_form_view_individual_volunteer(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    if back_menu_button.pressed(button):
        return previous_form(interface)
    elif button==DELETE_BUTTON_LABEL:
        return delete_volunteer_form(interface)
    elif button==EDIT_BUTTON_LABEL:
        return edit_volunteer_form(interface)
    elif button==EDIT_CADET_CONNECTIONS_BUTTON_LABEL:
        return edit_connections_form(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)


def previous_form(interface: abstractInterface)-> NewForm:
    return interface.get_new_display_form_for_parent_of_function(display_form_view_individual_volunteer)


def delete_volunteer_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_form_given_function(display_form_delete_individual_volunteer)


def edit_volunteer_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_form_given_function(display_form_edit_individual_volunteer)


def edit_connections_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_form_given_function(display_form_edit_cadet_volunteer_connections)

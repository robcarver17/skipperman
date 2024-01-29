from typing import Union


from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.abstract_logic_api import initial_state_form
from app.logic.abstract_interface import (
    abstractInterface,
)
from app.backend.volunteers import get_dict_of_existing_skills, get_connected_cadets
from app.logic.volunteers.volunteer_state import get_volunteer_from_state
from app.logic.volunteers.constants import *

from app.objects.volunteers import Volunteer

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
    #lines_of_allocations = list_of_lines_with_allocations(volunteer)

    connected = lines_for_connected_cadets(volunteer)
    skills = list_of_skills(volunteer)
    buttons = buttons_for_volunteer_form()
    return Form(
        ListOfLines([
            str(volunteer),
            _______________,
            skills,
            _______________,
            connected,
            #lines_of_allocations,
            _______________,
            buttons
        ])
    )

def list_of_lines_with_allocations_and_roles(volunteer: Volunteer) -> ListOfLines:
    #dict_of_allocations = get_dict_of_all_event_allocations_for_single_volunteer(cadet)
    #return ListOfLines(["Events helping at:", _______________]+
    #    ["%s: %s" % (str(event), group) for event, group in dict_of_allocations.items()]
    #)
    pass

def list_of_skills(volunteer: Volunteer) -> ListOfLines:
    skills = get_dict_of_existing_skills(volunteer)
    skills_held = [skill for skill, skill_held in skills.items() if skill_held]
    skills_not_held = [skill for skill, skill_held in skills.items() if not skill_held]

    return ListOfLines([
        "Skills held: %s" % ", ".join(skills_held),
        "Skills missing: %s" % ", ".join(skills_not_held),
    ])

def lines_for_connected_cadets(volunteer: Volunteer) -> Line:
    cadets = get_connected_cadets(volunteer)
    cadets_as_str = [str(cadet) for cadet in cadets]
    if len(cadets)==0:
        return Line([])
    return Line(
        "Connected to: %s" % ", ".join(cadets_as_str)
    )

def buttons_for_volunteer_form() -> Line:
    return Line([Button(BACK_BUTTON_LABEL), Button(EDIT_BUTTON_LABEL), Button(DELETE_BUTTON_LABEL), Button(EDIT_CADET_CONNECTIONS_BUTTON_LABEL)])


def post_form_view_individual_volunteer(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    if button==BACK_BUTTON_LABEL:
        return initial_state_form
    elif button==DELETE_BUTTON_LABEL:
        return NewForm(DELETE_VOLUNTEER_STAGE)
    elif button==EDIT_BUTTON_LABEL:
        return NewForm(EDIT_VOLUNTEER_STAGE)
    elif button==EDIT_CADET_CONNECTIONS_BUTTON_LABEL:
        return NewForm(EDIT_CONNECTIONS_STAGE)
    else:
        raise NotImplemented("Button not recognised")

from typing import Union
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.volunteers.constants import BACK_BUTTON_LABEL, SAVE_BUTTON_LABEL

from app.logic.volunteers.edit_volunteer import get_and_save_volunteer_skills_from_form, skills_form_entries
from app.logic.volunteers.volunteer_state import get_volunteer_from_state

from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.objects.volunteers import Volunteer


def display_form_edit_individual_volunteer_skills_from_rota(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    volunteer = get_volunteer_from_state(interface)

    return form_to_edit_individual_volunteer_skills_from_rota(volunteer=volunteer)

def form_to_edit_individual_volunteer_skills_from_rota(volunteer: Volunteer,
        ) -> Form:

    skills_entries = skills_form_entries(volunteer)

    footer_buttons = Line([Button(BACK_BUTTON_LABEL), Button(SAVE_BUTTON_LABEL)])

    return Form([
        ListOfLines([
            "Edit volunteer %s skills:" % volunteer.name,
            _______________,
            skills_entries,
            _______________,
            footer_buttons
        ])
    ])


def post_form_edit_individual_volunteer_skills_from_rota(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    if button==BACK_BUTTON_LABEL:
        return previous_form(interface)
    elif button==SAVE_BUTTON_LABEL:
        modify_volunteer_from_rota_given_form_contents(interface=interface)
        return previous_form(interface)
    else:
        raise Exception("Button %s not recognised" % button)



def modify_volunteer_from_rota_given_form_contents(interface: abstractInterface):
    volunteer = get_volunteer_from_state(interface)

    get_and_save_volunteer_skills_from_form(interface=interface, volunteer=volunteer)

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_edit_individual_volunteer_skills_from_rota)

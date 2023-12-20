from typing import Union

from app.data_access.data import data
from app.logic.forms_and_interfaces.abstract_form import Form, NewForm, Button, Line, ListOfLines, _______________, textInput, checkboxInput
from app.logic.abstract_logic_api import initial_state_form
from app.logic.forms_and_interfaces.abstract_interface import (
    abstractInterface,
)
from app.logic.volunteers.constants import *
from app.logic.volunteers.backend import get_volunteer_from_state, get_dict_of_existing_skills
from app.logic.volunteers.add_volunteer import get_volunteer_from_form
from app.objects.volunteers import Volunteer

def display_form_edit_individual_volunteer(
    interface: abstractInterface,
) -> Union[Form, NewForm]:

    try:
        volunteer = get_volunteer_from_state(interface)
    except:
        interface.log_error(
            "Volunteer selected no longer in list- someone else has deleted or file corruption?"
        )
        return initial_state_form

    form = form_to_edit_individual_volunteer(volunteer)

    return form

def form_to_edit_individual_volunteer(volunteer: Volunteer,
        ) -> Form:

    core_entries = core_volunteer_form_entries(volunteer)
    skills_entries = skills_form_entries(volunteer)

    footer_buttons = Line([Button(CANCEL_BUTTON_LABEL), Button(SAVE_BUTTON_LABEL)])

    return Form([
        ListOfLines([
            "Edit volunteer:",
            _______________,
            core_entries,
            _______________,
            skills_entries,
            _______________,
            footer_buttons
        ])
    ])

def core_volunteer_form_entries(volunteer: Volunteer) -> ListOfLines:
    first_name = textInput(
        input_label="First name", input_name=FIRST_NAME, value=volunteer.first_name
    )
    surname = textInput(
        input_label="Second name", input_name=SURNAME, value=volunteer.surname
    )

    return ListOfLines([Line(first_name), Line(surname)])

def skills_form_entries(volunteer: Volunteer):
    skills_dict = get_dict_of_existing_skills(volunteer)
    dict_of_labels = dict([(skill, skill) for skill in skills_dict.keys()])
    return checkboxInput(input_label="Volunteer skills:",
                         dict_of_checked=skills_dict,
                         dict_of_labels=dict_of_labels,
                         input_name=SKILLS)


def post_form_edit_individual_volunteer(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    if button==CANCEL_BUTTON_LABEL:
        return NewForm(VIEW_INDIVIDUAL_VOLUNTEER_STAGE)
    elif button==SAVE_BUTTON_LABEL:
        modify_volunteer_given_form_contents(interface=interface)
        ## have to go home as name might have change
        return initial_state_form

    else:
        raise Exception("Button %s not recognised" % button)

def modify_volunteer_given_form_contents(interface: abstractInterface):
    original_volunteer = get_volunteer_from_state(interface)

    get_and_save_core_volunteer_details_from_form(interface=interface, original_volunteer = original_volunteer)
    get_and_save_volunteer_skills_from_form(interface=interface, volunteer=original_volunteer)

def get_and_save_core_volunteer_details_from_form(interface: abstractInterface, original_volunteer: Volunteer):
    volunteer_details_from_form = get_volunteer_from_form(interface)
    volunteer_details_from_form.id = original_volunteer.id ## won't be in form

    list_of_volunteers = data.data_list_of_volunteers.read()
    index = list_of_volunteers.index_of_id(original_volunteer.id)
    list_of_volunteers[index] = volunteer_details_from_form
    data.data_list_of_volunteers.write(list_of_volunteers)

def get_and_save_volunteer_skills_from_form(interface: abstractInterface, volunteer: Volunteer):
    dict_of_skills = get_dict_of_skills_from_form(interface=interface, volunteer=volunteer)
    all_skills = data.data_list_of_volunteer_skills.read()
    all_skills.replace_skills_for_volunteer_with_new_skills_dict(volunteer_id=volunteer.id, dict_of_skills=dict_of_skills)
    data.data_list_of_volunteer_skills.write(all_skills)

def get_dict_of_skills_from_form(interface: abstractInterface, volunteer: Volunteer) -> dict:
    selected_skills = interface.value_of_multiple_options_from_form(SKILLS)
    existing_skills = get_dict_of_existing_skills(volunteer)
    for skill_name in existing_skills.keys():
        if skill_name in selected_skills:
            existing_skills[skill_name] = True
        else:
            existing_skills[skill_name] = False

    return existing_skills
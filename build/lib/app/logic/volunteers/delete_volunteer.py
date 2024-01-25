from typing import Union

from app.data_access.data import data
from app.logic.volunteers.volunteer_state import get_volunteer_from_state
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.abstract_logic_api import initial_state_form
from app.logic.abstract_interface import (
    abstractInterface,
)
from app.logic.volunteers.constants import *


def display_form_delete_individual_volunteer(
    interface: abstractInterface,
) -> Union[Form, NewForm]:

    try:
        volunteer = get_volunteer_from_state(interface)
    except:
        interface.log_error(
            "Volunteer selected no longer in list- someone else has deleted or file corruption?"
        )
        return initial_state_form

    return Form(ListOfLines([
        "Delete volunteer %s? Are you *really* sure? If they have been registered to help with past or current events will cause chaos!" % str(volunteer),
        "Might be better to edit instead",
        _______________,
        Line([
            Button(SURE_DELETE_BUTTON_LABEL),
            Button(CANCEL_BUTTON_LABEL)
        ])
    ]))


def post_form_delete_individual_volunteer(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    try:
        volunteer = get_volunteer_from_state(interface)
    except:
        interface.log_error(
            "Volunteer selected no longer in list- someone else has deleted or file corruption?"
        )
        return initial_state_form
    if button==CANCEL_BUTTON_LABEL:
        return NewForm(VIEW_INDIVIDUAL_VOLUNTEER_STAGE)
    elif button==SURE_DELETE_BUTTON_LABEL:
        delete_a_volunteer(volunteer)
        return initial_state_form

def delete_a_volunteer(volunteer):
    all_volunteers= data.data_list_of_volunteers.read()
    all_volunteers.pop_with_id(volunteer.id)
    data.data_list_of_volunteers.write(all_volunteers)
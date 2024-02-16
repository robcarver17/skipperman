from typing import Union

from app.backend.data.volunteers import delete_a_volunteer
from app.logic.volunteers.volunteer_state import get_volunteer_from_state
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.abstract_logic_api import initial_state_form, button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_interface import (
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
        return interface.get_new_display_form_for_parent_of_function(display_form_delete_individual_volunteer)
    elif button==SURE_DELETE_BUTTON_LABEL:
        delete_a_volunteer(volunteer)
        ## volunteer now missing so can't go to parent
        return initial_state_form
    else:
        button_error_and_back_to_initial_state_form(interface)

from typing import Union

from app.data_access.data import data
from app.logic.cadets.backend import get_cadet_from_state
from app.logic.forms_and_interfaces.abstract_form import Form, NewForm, Button, Line, ListOfLines, _______________
from app.logic.abstract_logic_api import initial_state_form
from app.logic.forms_and_interfaces.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.logic.events.allocation.backend.previous_allocations import get_dict_of_all_event_allocations_for_single_cadet
from app.logic.cadets.constants import *
from app.objects.cadets import Cadet


def display_form_delete_individual_cadet(
    interface: abstractInterface,
) -> Union[Form, NewForm]:

    try:
        cadet = get_cadet_from_state(interface)
    except:
        interface.log_error(
            "Cadet selected no longer in list- someone else has deleted or file corruption?"
        )
        return initial_state_form

    return Form(ListOfLines([
        "Delete cadet %s? Are you *really* sure? If they have been registered to an event will cause chaos!" % str(cadet),
        "Might be better to edit instead",
        _______________,
        Line([
            Button(SURE_DELETE_BUTTON_LABEL),
            Button(CANCEL_BUTTON_LABEL)
        ])
    ]))


def post_form_delete_individual_cadet(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    try:
        cadet = get_cadet_from_state(interface)
    except:
        interface.log_error(
            "Cadet selected no longer in list- someone else has deleted or file corruption?"
        )
        return initial_state_form
    if button==CANCEL_BUTTON_LABEL:
        return NewForm(VIEW_INDIVIDUAL_CADET_STAGE)
    elif button==SURE_DELETE_BUTTON_LABEL:
        delete_a_cadet(cadet)
        return initial_state_form
def delete_a_cadet(cadet):
    all_cadets = data.data_list_of_cadets.read()
    all_cadets.pop_with_id(cadet.id)
    data.data_list_of_cadets.write(all_cadets)
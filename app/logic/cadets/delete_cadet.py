from typing import Union

from app.logic.cadets.cadet_state_storage import get_cadet_from_state
from app.backend.cadets import delete_a_cadet
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.abstract_logic_api import initial_state_form
from app.logic.abstract_interface import (
    abstractInterface,
)
from app.logic.cadets.constants import *


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

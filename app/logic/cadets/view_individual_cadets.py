from typing import Union

from app.logic.cadets.backend import get_cadet_from_state
from app.logic.forms_and_interfaces.abstract_form import Form, NewForm, Button, Line, ListOfLines, _______________
from app.logic.abstract_logic_api import initial_state_form
from app.logic.forms_and_interfaces.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.logic.events.allocation.backend.previous_allocations import get_dict_of_all_event_allocations_for_single_cadet
from app.logic.cadets.constants import EDIT_BUTTON_LABEL, DELETE_BUTTON_LABEL, BACK_BUTTON_LABEL, EDIT_INDIVIDUAL_CADET_STAGE, DELETE_INDIVIDUAL_CADET_STAGE
from app.objects.cadets import Cadet


def display_form_view_individual_cadet(
    interface: abstractInterface,
) -> Union[Form, NewForm]:

    try:
        cadet = get_cadet_from_state(interface)
    except:
        interface.log_error(
            "Cadet selected no longer in list- someone else has deleted or file corruption?"
        )
        return initial_state_form

    return display_form_for_selected_cadet(
        cadet = cadet, interface=interface
    )


def post_form_view_individual_cadet(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    if button==BACK_BUTTON_LABEL:
        return initial_state_form
    elif button==DELETE_BUTTON_LABEL:
        return NewForm(DELETE_INDIVIDUAL_CADET_STAGE)
    elif button==EDIT_BUTTON_LABEL:
        return NewForm(EDIT_INDIVIDUAL_CADET_STAGE)
    else:
        raise NotImplemented("Button not recognised")


def display_form_for_selected_cadet(
    cadet: Cadet, interface: abstractInterface
) -> Form:
    lines_of_allocations = list_of_lines_with_allocations(cadet)
    buttons = buttons_for_cadet_form()
    return Form(
        ListOfLines([
            str(cadet),
            _______________,
            lines_of_allocations,
            _______________,
            buttons
        ])
    )

def list_of_lines_with_allocations(cadet: Cadet) -> ListOfLines:
    dict_of_allocations = get_dict_of_all_event_allocations_for_single_cadet(cadet)
    return ListOfLines(["Events registered at:", _______________]+
        ["%s: %s" % (str(event), group) for event, group in dict_of_allocations.items()]
    )

def buttons_for_cadet_form() -> Line:
    return Line([Button(BACK_BUTTON_LABEL), Button(EDIT_BUTTON_LABEL), Button(DELETE_BUTTON_LABEL)])



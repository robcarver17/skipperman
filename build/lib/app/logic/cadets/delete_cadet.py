

from typing import Union

from app.frontend.shared.cadet_state import get_cadet_from_state
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import Button, CANCEL_BUTTON_LABEL
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.frontend.form_handler import initial_state_form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)


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
        "Might be better to edit or merge instead",
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
        return previous_form(interface)

    elif button==SURE_DELETE_BUTTON_LABEL:
        interface.log_error("DELETION NOT ALLOWED")
        ## Cadet gone missing so back to list of all cadets
        ## Cadet gone missing so back to list of all cadets
        return initial_state_form

def previous_form(interface:abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_delete_individual_cadet)


SURE_DELETE_BUTTON_LABEL = "Sure you want to delete?"

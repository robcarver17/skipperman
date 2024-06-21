from typing import Union

from app.data_access.configuration.fixed import CANCEL_KEYBOARD_SHORTCUT, SAVE_KEYBOARD_SHORTCUT
from app.logic.cadets.cadet_state_storage import get_cadet_from_state
from app.backend.cadets import modify_cadet
from app.objects.abstract_objects.abstract_form import Form, NewForm, checkboxInput
from app.objects.abstract_objects.abstract_buttons import Button, ButtonBar, SAVE_BUTTON_LABEL, CANCEL_BUTTON_LABEL
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.logic.abstract_logic_api import initial_state_form, button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

from app.logic.cadets.add_cadet import CadetAndVerificationText, get_cadet_from_form, form_fields_for_add_cadet

QUALIFICATIONS = "Qualifications"

def display_form_edit_individual_cadet(
    interface: abstractInterface,
) -> Union[Form, NewForm]:

    try:
        cadet = get_cadet_from_state(interface)
    except:
        interface.log_error(
            "Cadet selected no longer in list- someone else has deleted or file corruption?"
        )
        return initial_state_form

    footer_buttons = ButtonBar([Button(CANCEL_BUTTON_LABEL, nav_button=True, shortcut=CANCEL_KEYBOARD_SHORTCUT), Button(SAVE_BUTTON_LABEL, nav_button=True, shortcut=SAVE_KEYBOARD_SHORTCUT)])
    cadet_and_text = CadetAndVerificationText(
        cadet=cadet,
        verification_text=""
    )

    form_fields = form_fields_for_add_cadet(cadet_and_text.cadet)

    list_of_lines_inside_form = ListOfLines(
        [
            "Edit cadet",
            _______________,
            form_fields,
            _______________,
            cadet_and_text.verification_text,
            _______________,
            footer_buttons,
        ]
    )

    return Form(list_of_lines_inside_form)


def post_form_edit_individual_cadet(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    if button==CANCEL_BUTTON_LABEL:
        return previous_form(interface)
    elif button==SAVE_BUTTON_LABEL:
        modify_cadet_given_form_contents(interface)
        interface._DONT_CALL_DIRECTLY_USE_FLUSH_save_stored_items()
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_edit_individual_cadet)


def modify_cadet_given_form_contents(interface: abstractInterface):
    modify_cadet_data_given_form_contents(interface)


def modify_cadet_data_given_form_contents(interface: abstractInterface):
    original_cadet = get_cadet_from_state(interface)
    new_cadet = get_cadet_from_form(interface)
    modify_cadet(interface=interface, cadet_id = original_cadet.id, new_cadet = new_cadet)



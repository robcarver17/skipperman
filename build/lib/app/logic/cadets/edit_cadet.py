from typing import Union

from app.data_access.data import data
from app.logic.cadets.backend import get_cadet_from_state, get_list_of_cadets
from app.logic.forms_and_interfaces.abstract_form import Form, NewForm, Button, Line, ListOfLines, _______________
from app.logic.abstract_logic_api import initial_state_form
from app.logic.forms_and_interfaces.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.logic.events.allocation.backend.previous_allocations import get_dict_of_all_event_allocations_for_single_cadet
from app.logic.cadets.constants import *
from app.objects.cadets import Cadet
from app.logic.cadets.add_cadet import get_add_cadet_form_with_information_passed, CadetAndVerificationText, get_cadet_from_form

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
    footer_buttons = Line([Button(CANCEL_BUTTON_LABEL), Button(SAVE_BUTTON_LABEL)])
    cadet_and_text = CadetAndVerificationText(
        cadet=cadet,
        verification_text=""
    )
    form = get_add_cadet_form_with_information_passed(footer_buttons=footer_buttons,
                                                      cadet_and_text=cadet_and_text,
                                                      header_text="Edit existing cadet")

    return form

def post_form_edit_individual_cadet(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    if button==CANCEL_BUTTON_LABEL:
        return NewForm(VIEW_INDIVIDUAL_CADET_STAGE)
    elif button==SAVE_BUTTON_LABEL:
        modify_cadet_given_form_contents(interface)
        ## We can't go to view individual cadet or we'd get a cadet not found error
        return initial_state_form
    else:
        raise Exception("Button %s not recognised" % button)

def modify_cadet_given_form_contents(interface: abstractInterface):
    original_cadet = get_cadet_from_state(interface)
    cadet_details = get_cadet_from_form(interface)
    cadet_details.id = original_cadet.id
    list_of_cadets = get_list_of_cadets()
    list_of_cadets.replace_with_new_object(cadet_details)

    data.data_list_of_cadets.write(list_of_cadets)
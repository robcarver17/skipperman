from typing import Union

from app.logic.cadets.cadet_state_storage import get_cadet_from_state
from app.logic.cadets.delete_cadet import display_form_delete_individual_cadet
from app.logic.cadets.edit_cadet import display_form_edit_individual_cadet
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.abstract_logic_api import initial_state_form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.backend.group_allocations.previous_allocations import get_dict_of_all_event_allocations_for_single_cadet
from app.logic.cadets.constants import EDIT_BUTTON_LABEL, DELETE_BUTTON_LABEL, BACK_BUTTON_LABEL
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
        cadet = cadet
    )


def display_form_for_selected_cadet(
    cadet: Cadet
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



def post_form_view_individual_cadet(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    if button==BACK_BUTTON_LABEL:
        return initial_state_form
    elif button==DELETE_BUTTON_LABEL:
        return form_for_delete_cadet(interface)
    elif button==EDIT_BUTTON_LABEL:
        return form_for_edit_cadet(interface)
    else:
        return return_to_previous_form(interface)

def form_for_delete_cadet(interface: abstractInterface)->NewForm:
    return interface.get_new_form_given_function(display_form_delete_individual_cadet)

def form_for_edit_cadet(interface: abstractInterface)->NewForm:
    return interface.get_new_form_given_function(display_form_edit_individual_cadet)


def return_to_previous_form(interface: abstractInterface)->NewForm:
    return interface.get_new_display_form_for_parent_of_function(display_form_view_individual_cadet)

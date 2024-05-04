from typing import Union

from app.backend.data.qualification import list_of_named_qualifications_for_cadet, get_list_of_qualification_names, \
    update_qualifications_for_cadet
from app.objects.cadets import Cadet

from app.logic.cadets.cadet_state_storage import get_cadet_from_state
from app.backend.cadets import modify_cadet
from app.objects.abstract_objects.abstract_form import Form, NewForm, checkboxInput
from app.objects.abstract_objects.abstract_buttons import Button, ButtonBar
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.logic.abstract_logic_api import initial_state_form, button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.logic.cadets.constants import *
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

    footer_buttons = ButtonBar([Button(CANCEL_BUTTON_LABEL, nav_button=True), Button(SAVE_BUTTON_LABEL, nav_button=True)])
    cadet_and_text = CadetAndVerificationText(
        cadet=cadet,
        verification_text=""
    )

    form_fields = form_fields_for_add_cadet(cadet_and_text.cadet)
    qualifications = checkbox_for_qualifications(cadet)

    list_of_lines_inside_form = ListOfLines(
        [
            "Edit cadet",
            _______________,
            form_fields,
            qualifications,
            _______________,
            cadet_and_text.verification_text,
            _______________,
            footer_buttons,
        ]
    )

    return Form(list_of_lines_inside_form)

def checkbox_for_qualifications(cadet: Cadet)-> checkboxInput:
    qualifications = list_of_named_qualifications_for_cadet(cadet)
    all_qualifications = get_list_of_qualification_names()
    dict_of_labels = dict([(qual,qual) for qual in all_qualifications])
    dict_of_checked = {}
    for qual in all_qualifications:
        if qual in qualifications:
            dict_of_checked[qual]=True
        else:
            dict_of_checked[qual]= False

    return checkboxInput(
        input_label="Qualifications (use ticksheets to add, only remove here if errors made)",
        input_name=QUALIFICATIONS,
        dict_of_labels=dict_of_labels,
        dict_of_checked=dict_of_checked,
    )

def post_form_edit_individual_cadet(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    if button==CANCEL_BUTTON_LABEL:
        return previous_form(interface)
    elif button==SAVE_BUTTON_LABEL:
        modify_cadet_given_form_contents(interface)
        interface.save_stored_items()
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_edit_individual_cadet)


def modify_cadet_given_form_contents(interface: abstractInterface):
    modify_cadet_data_given_form_contents(interface)
    modify_qualifications(interface)

def modify_cadet_data_given_form_contents(interface: abstractInterface):
    original_cadet = get_cadet_from_state(interface)
    new_cadet = get_cadet_from_form(interface)
    modify_cadet(interface=interface, cadet_id = original_cadet.id, new_cadet = new_cadet)


def modify_qualifications(interface: abstractInterface):
    cadet = get_cadet_from_state(interface)
    list_of_qualification_names_for_this_cadet = interface.value_of_multiple_options_from_form(QUALIFICATIONS)
    update_qualifications_for_cadet(cadet=cadet, list_of_qualification_names_for_this_cadet=list_of_qualification_names_for_this_cadet)
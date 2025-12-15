from typing import Union

from app.frontend.shared.cadet_state import get_cadet_from_state
from app.backend.cadets.add_edit_cadet import modify_cadet
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    cancel_menu_button,
    save_menu_button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.frontend.form_handler import (
    initial_state_form,
    button_error_and_back_to_initial_state_form,
)
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

from app.frontend.shared.add_edit_cadet_form import (
    CadetAndVerificationText,
    form_fields_for_add_cadet,
    get_cadet_from_form,
)
from app.objects.utilities.exceptions import MISSING_FROM_FORM

QUALIFICATIONS = "Qualifications"


def display_form_edit_individual_cadet(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    try:
        cadet = get_cadet_from_state(interface)
    except:
        interface.log_error(
            "Sailor selected no longer in list- someone else has deleted or file corruption?"
        )
        return initial_state_form

    footer_buttons = ButtonBar([cancel_menu_button, save_menu_button, help_button])

    cadet_and_text = CadetAndVerificationText(cadet=cadet, verification_text="")

    form_fields = form_fields_for_add_cadet(cadet_and_text.cadet)

    list_of_lines_inside_form = ListOfLines(
        [
            ButtonBar([help_button]),
            "Edit sailor",
            _______________,
            form_fields,
            _______________,
            cadet_and_text.verification_text,
            _______________,
            footer_buttons,
        ]
    )

    return Form(list_of_lines_inside_form)


help_button = HelpButton("view_and_edit_individual_cadet_help")


def post_form_edit_individual_cadet(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button_pressed = interface.last_button_pressed()
    if cancel_menu_button.pressed(button_pressed):
        return previous_form(interface)
    elif save_menu_button.pressed(button_pressed):
        modify_cadet_given_form_contents(interface)
        interface.DEPRECATE_flush_and_clear()
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_edit_individual_cadet
    )


def modify_cadet_given_form_contents(interface: abstractInterface):
    existing_cadet = get_cadet_from_state(interface)
    new_cadet = get_cadet_from_form(interface)
    if new_cadet is MISSING_FROM_FORM:
        interface.log_error("Can't find cadet details in form")
        return
    modify_cadet(
        object_store=interface.object_store,
        existing_cadet=existing_cadet,
        new_cadet=new_cadet,
    )

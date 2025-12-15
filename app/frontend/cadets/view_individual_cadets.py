from typing import Union

from app.backend.cadets.cadet_committee import get_cadet_on_committee_status

from app.backend.qualifications_and_ticks.qualifications_for_cadet import (
    sorted_list_of_named_qualifications_for_cadet,
)
from app.frontend.shared.cadet_state import get_cadet_from_state
from app.frontend.cadets.edit_cadet import display_form_edit_individual_cadet
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    back_menu_button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.frontend.form_handler import initial_state_form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.backend.groups.previous_groups import (
    DEPRECATE_get_dict_of_all_event_allocations_for_single_cadet, get_dict_of_all_event_allocations_for_single_cadet,
)
from app.objects.cadets import Cadet


def display_form_view_individual_cadet(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    try:
        cadet = get_cadet_from_state(interface)
    except:
        interface.log_error(
            "Sailor selected no longer in list- someone else has deleted or file corruption?"
        )
        return initial_state_form

    return display_form_for_selected_cadet(interface=interface, cadet=cadet)


def display_form_for_selected_cadet(interface: abstractInterface, cadet: Cadet) -> Form:
    lines_of_allocations = list_of_lines_with_allocations(
        interface=interface, cadet=cadet
    )
    qualifications_str = qualifications_line(interface=interface, cadet=cadet)
    committee_str = get_cadet_on_committee_status(
        object_store=interface.object_store, cadet=cadet
    )
    buttons = buttons_for_view_individual_cadet_form()
    return Form(
        ListOfLines(
            [
                buttons,
                _______________,
                str(cadet),
                _______________,
                lines_of_allocations,
                _______________,
                qualifications_str,
                _______________,
                committee_str,
            ]
        )
    )


def list_of_lines_with_allocations(
    interface: abstractInterface, cadet: Cadet
) -> ListOfLines:
    dict_of_allocations = get_dict_of_all_event_allocations_for_single_cadet(
        object_store=interface.object_store,
        cadet=cadet
    )
    return ListOfLines(
        ["Events registered at:", _______________]
        + [
            Line("%s: %s" % (str(event), group))
            for event, group in dict_of_allocations.items()
        ]
    )


def qualifications_line(interface: abstractInterface, cadet: Cadet) -> Line:
    qualifications = sorted_list_of_named_qualifications_for_cadet(
        object_store=interface.object_store, cadet=cadet
    )
    qualifications_str = ", ".join(qualifications)

    return Line(["Qualifications: %s" % qualifications_str])


def buttons_for_view_individual_cadet_form() -> ButtonBar:
    return ButtonBar([back_menu_button, edit_cadet_button, help_button])


EDIT_BUTTON_LABEL = "Edit"
edit_cadet_button = Button(EDIT_BUTTON_LABEL, nav_button=True)
help_button = HelpButton("view_and_edit_individual_cadet_help")


def post_form_view_individual_cadet(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    if back_menu_button.pressed(button):
        return initial_state_form
    elif edit_cadet_button.pressed(button):
        return form_for_edit_cadet(interface)
    else:
        return return_to_previous_form(interface)


def form_for_edit_cadet(interface: abstractInterface) -> NewForm:
    return interface.get_new_form_given_function(display_form_edit_individual_cadet)


def return_to_previous_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_form_view_individual_cadet
    )

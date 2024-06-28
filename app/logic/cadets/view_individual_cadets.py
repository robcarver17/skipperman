from typing import Union

from app.backend.data.cadets_at_id_level import CadetData

from app.backend.ticks_and_qualifications.qualifications import (
    sorted_list_of_named_qualifications_for_cadet,
)
from app.logic.shared.cadet_state_storage import get_cadet_from_state
from app.logic.cadets.edit_cadet import display_form_edit_individual_cadet
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    back_menu_button,
)
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.logic.abstract_logic_api import initial_state_form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.backend.group_allocations.previous_allocations import (
    get_dict_of_all_event_allocations_for_single_cadet,
)
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

    return display_form_for_selected_cadet(interface=interface, cadet=cadet)


def display_form_for_selected_cadet(interface: abstractInterface, cadet: Cadet) -> Form:
    lines_of_allocations = list_of_lines_with_allocations(
        interface=interface, cadet=cadet
    )
    qualifications_str = qualifications_line(interface=interface, cadet=cadet)
    committee_str = get_committee_string(interface=interface, cadet=cadet)
    buttons = buttons_for_cadet_form()
    return Form(
        ListOfLines(
            [
                str(cadet),
                _______________,
                lines_of_allocations,
                qualifications_str,
                committee_str,
                _______________,
                buttons,
            ]
        )
    )


def list_of_lines_with_allocations(
    interface: abstractInterface, cadet: Cadet
) -> ListOfLines:
    dict_of_allocations = get_dict_of_all_event_allocations_for_single_cadet(
        data_layer=interface.data, cadet=cadet, remove_unallocated=True
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
        interface=interface, cadet=cadet
    )
    qualifications_str = ", ".join(qualifications)

    return Line(["Qualifications: %s" % qualifications_str])


def get_committee_string(interface: abstractInterface, cadet: Cadet) -> Line:
    cadet_data = CadetData(interface.data)
    return Line(cadet_data.cadet_on_committee_status_str(cadet))


def buttons_for_cadet_form() -> ButtonBar:
    return ButtonBar([back_menu_button, edit_cadet_button])


EDIT_BUTTON_LABEL = "Edit"
edit_cadet_button = Button(EDIT_BUTTON_LABEL, nav_button=True)


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

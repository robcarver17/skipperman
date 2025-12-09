from app.frontend.shared.cadet_state import update_state_for_specific_cadet

from app.backend.administration_and_utilities.delete_cadets import (
    delete_cadet_in_data_and_return_warnings,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.shared.cadet_state import get_cadet_from_state
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import Form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.cadets import Cadet


def display_deleting_cadet_process(interface: abstractInterface):
    cadet_to_delete = get_cadet_to_delete_from_state(interface)
    warnings = delete_cadet_in_data_but_do_not_save_cache_and_return_warnings(
        interface, cadet_to_delete=cadet_to_delete
    )

    return Form(
        ListOfLines(
            [Heading("Deleting %s" % (cadet_to_delete)), _______________]
            + warnings
            + [Line([yes_button, cancel_button])]
        ).add_Lines()
    )


def post_deleting_cadets_process(interface: abstractInterface):
    button_pressed = interface.last_button_pressed()
    print("pressed %s" % button_pressed)
    if yes_button.pressed(button_pressed):
        
        cadet_to_delete = get_cadet_to_delete_from_state(interface)
        delete_cadet_in_data_and_return_warnings(
            interface.object_store, cadet_to_delete=cadet_to_delete
        )
        interface.flush_and_clear()  ## saves
        message = "Deletion done"
    elif cancel_button.pressed(button_pressed):
        message = "Deletion cancelled"
    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.log_error(message)

    return interface.get_new_display_form_for_parent_of_function(display_deleting_cadet_process)


def delete_cadet_in_data_but_do_not_save_cache_and_return_warnings(
    interface: abstractInterface, cadet_to_delete: Cadet
) -> ListOfLines:
    warnings = delete_cadet_in_data_and_return_warnings(
        interface.object_store, cadet_to_delete=cadet_to_delete
    )

    return ListOfLines(warnings).add_Lines()


yes_button = Button("Yes, go ahead with deletion")
cancel_button = Button("No, cancel")


def get_cadet_to_delete_from_state(interface: abstractInterface) -> Cadet:
    return get_cadet_from_state(interface)  ## to make it clearer


def set_cadet_to_delete_in_state(interface: abstractInterface, cadet: Cadet):
    update_state_for_specific_cadet(interface=interface, cadet=cadet)

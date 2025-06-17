from app.backend.administration_and_utilities.delete_volunteers import (
    delete_volunteer_in_data_and_return_warnings,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.shared.volunteer_state import (
    get_volunteer_from_state,
    update_state_for_specific_volunteer,
)
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import Form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    Line,
    _______________,
)
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.volunteers import Volunteer


def display_deleting_volunteer_process(interface: abstractInterface):
    volunteer_to_delete = get_volunteer_to_delete_from_state(interface)
    warnings = delete_volunteer_in_data_but_do_not_save_cache_and_return_warnings(
        interface, volunteer_to_delete=volunteer_to_delete
    )

    return Form(
        ListOfLines(
            [Heading("Deleting %s" % (volunteer_to_delete)), _______________]
            + warnings
            + [Line([yes_button, cancel_button])]
        ).add_Lines()
    )


def post_deleting_volunteers_process(interface: abstractInterface):
    button_pressed = interface.last_button_pressed()
    print("pressed %s" % button_pressed)
    if yes_button.pressed(button_pressed):
        interface.flush_cache_to_store()  ## saves
        message = "Deletion done, click to return to menu"
    elif cancel_button.pressed(button_pressed):
        interface.clear_cache()  ## does not save
        message = "Deletion cancelled, click to return to menu"
    else:
        return button_error_and_back_to_initial_state_form(interface)

    return form_with_message_and_finished_button(interface=interface, message=message)


def delete_volunteer_in_data_but_do_not_save_cache_and_return_warnings(
    interface: abstractInterface, volunteer_to_delete: Volunteer
) -> ListOfLines:

    warnings = delete_volunteer_in_data_and_return_warnings(
        interface.object_store, volunteer_to_delete=volunteer_to_delete
    )

    return ListOfLines(warnings).add_Lines()


yes_button = Button("Yes, go ahead with deletion")
cancel_button = Button("No, cancel")


def get_volunteer_to_delete_from_state(interface: abstractInterface) -> Volunteer:
    return get_volunteer_from_state(interface)  ## to make it clearer


def set_volunteer_to_delete_in_state(
    interface: abstractInterface, volunteer: Volunteer
):
    update_state_for_specific_volunteer(interface=interface, volunteer=volunteer)

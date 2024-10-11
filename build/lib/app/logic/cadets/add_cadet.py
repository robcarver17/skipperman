from typing import Union

from app.frontend.shared.add_edit_cadet_form import (
    get_add_cadet_form,
    final_submit_button,
    check_details_button,
    add_cadet_from_form_to_data,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import cancel_menu_button

from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.frontend.form_handler import (
    initial_state_form,
    button_error_and_back_to_initial_state_form,
)


def display_form_add_cadet(interface: abstractInterface) -> Union[Form, NewForm]:
    return get_add_cadet_form(interface=interface, first_time_displayed=True)


def post_form_add_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()

    if check_details_button.pressed(last_button_pressed):
        ## verify results, display form again
        return get_add_cadet_form(interface=interface, first_time_displayed=False)

    elif final_submit_button.pressed(last_button_pressed):
        return process_form_when_cadet_verified(interface)

    elif cancel_menu_button.pressed(last_button_pressed):
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)


def previous_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(display_form_add_cadet)


def process_form_when_cadet_verified(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    try:
        cadet = add_cadet_from_form_to_data(interface)
    except Exception as e:
        ## should never happen as we have to be verified to get here, but still
        interface.log_error(
            "Can't add this cadet, something weird has happened error code %s, try again"
            % str(e)
        )
        return initial_state_form

    interface.flush_cache_to_store()

    return form_with_message_and_finished_button(
        "Added cadet %s" % str(cadet),
        interface=interface,
        function_whose_parent_go_to_on_button_press=display_form_add_cadet,
    )



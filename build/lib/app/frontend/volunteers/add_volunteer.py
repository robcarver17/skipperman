from typing import Union

from app.objects.abstract_objects.abstract_lines import ListOfLines

from app.frontend.form_handler import (
    initial_state_form,
    button_error_and_back_to_initial_state_form,
)
from app.frontend.shared.add_edit_or_choose_volunteer_form import (
    add_volunteer_from_form_to_data,
    verify_form_with_volunteer_details,
    get_add_volunteer_form_with_information_passed,
    get_footer_buttons_for_add_volunteer_form,
    final_submit_button,
    check_submit_button,
)

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import (
    cancel_menu_button,
    ButtonBar,
    HelpButton,
)
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)


def display_form_add_volunteer(interface: abstractInterface) -> Form:
    ## Called by frontend API only once, subsequently we are responding to button presses
    return get_add_volunteer_form(interface=interface, first_time_displayed=True)


def get_add_volunteer_form(
    interface: abstractInterface, first_time_displayed: bool = True
) -> Form:
    if first_time_displayed:
        footer_buttons = get_footer_buttons_for_add_volunteer_form(form_is_empty=True)
        return get_add_volunteer_form_with_information_passed(
            footer_buttons=footer_buttons, header_text=header_text
        )
    else:
        volunteer_and_text = verify_form_with_volunteer_details(interface)
        form_is_empty = volunteer_and_text.is_default
        footer_buttons = get_footer_buttons_for_add_volunteer_form(form_is_empty)

        return get_add_volunteer_form_with_information_passed(
            volunteer_and_text=volunteer_and_text,
            footer_buttons=footer_buttons,
            header_text=header_text,
        )


help_button = HelpButton("add_new_volunteer_help")
header_text = ListOfLines([ButtonBar([help_button]), "Add a new volunteer"]).add_Lines()


def post_form_add_volunteer(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by Logic API when buttons pressed

    last_button_pressed = interface.last_button_pressed()
    if cancel_menu_button.pressed(last_button_pressed):
        return previous_form(interface)

    if check_submit_button.pressed(last_button_pressed):
        ## verify results, display form again
        return get_add_volunteer_form(interface=interface, first_time_displayed=False)

    elif final_submit_button.pressed(last_button_pressed):
        return process_form_when_volunteer_verified(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_add_volunteer
    )


def process_form_when_volunteer_verified(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    try:
        volunteer = add_volunteer_from_form_to_data(interface)
    except Exception as e:
        ## should never happen as we have to be verified to get here, but still
        interface.log_error(
            "Can't add this volunteer, something weird has happened error code %s, try again"
            % str(e)
        )
        return initial_state_form

    interface.log_error("Added volunteer %s" % str(volunteer))

    return interface.get_new_display_form_for_parent_of_function(display_form_add_volunteer)

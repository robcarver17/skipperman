from copy import copy
from dataclasses import dataclass
from typing import Union

from app.backend.volunteers.volunteers import (
    verify_volunteer_and_warn,
    add_new_verified_volunteer,
)
from app.logic.abstract_logic_api import (
    initial_state_form,
    button_error_and_back_to_initial_state_form,
)
from app.objects.volunteers import Volunteer, default_volunteer

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    textInput,
)
from app.objects.abstract_objects.abstract_buttons import (
    CANCEL_BUTTON_LABEL,
    Button,
    ButtonBar,
    cancel_menu_button,
)
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.logic.volunteers.constants import *


def display_form_add_volunteer(interface: abstractInterface) -> Form:
    ## Called by logic API only once, subsequently we are responding to button presses
    return get_add_volunteer_form(interface=interface, first_time_displayed=True)


def post_form_add_volunteer(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by Logic API when buttons pressed

    last_button_pressed = interface.last_button_pressed()
    if cancel_menu_button.pressed(last_button_pressed):
        return previous_form(interface)

    if last_button_pressed == CHECK_BUTTON_LABEL:
        ## verify results, display form again
        return get_add_volunteer_form(interface=interface, first_time_displayed=False)

    elif last_button_pressed == FINAL_ADD_BUTTON_LABEL:
        return process_form_when_volunteer_verified(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_add_volunteer
    )


def get_add_volunteer_form(
    interface: abstractInterface, first_time_displayed: bool = True
) -> Form:
    if first_time_displayed:
        footer_buttons = get_footer_buttons_for_add_volunteer_form(form_is_empty=True)
        return get_add_volunteer_form_with_information_passed(
            footer_buttons=footer_buttons
        )
    else:
        volunteer_and_text = verify_form_with_volunteer_details(interface)
        form_is_empty = volunteer_and_text.is_default
        footer_buttons = get_footer_buttons_for_add_volunteer_form(form_is_empty)

        return get_add_volunteer_form_with_information_passed(
            volunteer_and_text=volunteer_and_text,
            footer_buttons=footer_buttons,
        )


@dataclass
class VolunteerAndVerificationText:
    volunteer: Volunteer
    verification_text: str = ""

    @property
    def is_default(self) -> bool:
        return self.volunteer is default_volunteer


default_volunteer_and_text = VolunteerAndVerificationText(
    volunteer=default_volunteer, verification_text=""
)


def get_add_volunteer_form_with_information_passed(
    footer_buttons: Union[Line, ListOfLines, ButtonBar],
    header_text: ListOfLines = "Add a new volunteer",
    volunteer_and_text: VolunteerAndVerificationText = default_volunteer_and_text,  ## if blank
) -> Form:
    form_fields = form_fields_for_add_volunteer(volunteer_and_text.volunteer)

    list_of_lines_inside_form = ListOfLines(
        [
            header_text,
            _______________,
            form_fields,
            _______________,
            volunteer_and_text.verification_text,
            _______________,
            footer_buttons,
        ]
    )

    return Form(list_of_lines_inside_form)


def form_fields_for_add_volunteer(volunteer: Volunteer):
    first_name = textInput(
        input_label="First name", input_name=FIRST_NAME, value=volunteer.first_name
    )
    surname = textInput(
        input_label="Second name", input_name=SURNAME, value=volunteer.surname
    )
    form_fields = ListOfLines([Line(first_name), Line(surname)])

    return form_fields


def verify_form_with_volunteer_details(
    interface: abstractInterface, default=default_volunteer
) -> VolunteerAndVerificationText:
    try:
        volunteer = get_volunteer_from_form(interface)
        verify_text = verify_volunteer_and_warn(
            interface=interface, volunteer=volunteer
        )
    except Exception as e:
        volunteer = copy(default)
        verify_text = "Doesn't appear to be a valid volunteer error code %s" % str(e)

    return VolunteerAndVerificationText(
        volunteer=volunteer, verification_text=verify_text
    )


def get_volunteer_from_form(interface: abstractInterface) -> Volunteer:
    first_name = interface.value_from_form(FIRST_NAME).strip().title()
    surname = interface.value_from_form(SURNAME).strip().title()

    return Volunteer.new(first_name=first_name, surname=surname)


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

    return form_with_message_and_finished_button(
        "Added volunteer %s" % str(volunteer),
        interface=interface,
        function_whose_parent_go_to_on_button_press=display_form_add_volunteer,
    )


def add_volunteer_from_form_to_data(interface) -> Volunteer:
    volunteer = get_volunteer_from_form(interface)
    add_new_verified_volunteer(volunteer=volunteer, interface=interface)
    interface.flush_cache_to_store()

    return volunteer


def get_footer_buttons_for_add_volunteer_form(form_is_empty: bool) -> ButtonBar:
    final_submit = Button(FINAL_ADD_BUTTON_LABEL, nav_button=True)
    check_submit = Button(CHECK_BUTTON_LABEL, nav_button=True)

    if form_is_empty:
        return ButtonBar([cancel_menu_button, check_submit])
    else:
        return ButtonBar([cancel_menu_button, check_submit, final_submit])

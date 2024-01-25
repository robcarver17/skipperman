from copy import copy
from dataclasses import dataclass
from typing import Union

from app.data_access.data import data
from app.logic.abstract_logic_api import initial_state_form
from app.objects.volunteers import Volunteer, default_volunteer
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    textInput,
)
from app.objects.abstract_objects.abstract_buttons import cancel_button, Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.abstract_interface import abstractInterface, form_with_message_and_finished_button
from app.logic.volunteers.constants import *

def display_form_add_volunteer(    interface: abstractInterface, first_time_displayed: bool = True
) -> Form:

    if first_time_displayed:
        ## hasn't been displayed before, will have no defaults
        return get_add_volunteer_form(interface=interface, first_time_displayed=True)

    last_button_pressed = interface.last_button_pressed()

    if last_button_pressed == CHECK_BUTTON_LABEL:
        ## verify results, display form again
        return get_add_volunteer_form(interface=interface, first_time_displayed=False)

    elif last_button_pressed == FINAL_ADD_BUTTON_LABEL:
        return process_form_when_volunteer_verified(interface)

    else:
        interface.log_error(
            "Uknown button pressed %s - shouldn't happen!" % last_button_pressed
        )
        return initial_state_form


def get_add_volunteer_form(    interface: abstractInterface, first_time_displayed: bool = True) -> Form:
    if first_time_displayed:
        footer_buttons = get_footer_buttons_for_add_volunteer_form(form_is_empty=True)
        return get_add_volunteer_form_with_information_passed(footer_buttons=footer_buttons)
    else:
        volunteer_and_text = verify_form_with_volunteer_details(interface)
        form_is_empty = volunteer_and_text.is_default
        footer_buttons = get_footer_buttons_for_add_volunteer_form(form_is_empty)

        return get_add_volunteer_form_with_information_passed(
            volunteer_and_text=volunteer_and_text,
            footer_buttons=footer_buttons,
        )



def post_form_add_volunteer(interface: abstractInterface) -> Union[Form, NewForm]:
    return display_form_add_volunteer(interface, first_time_displayed=False)





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
    footer_buttons: Union[Line, ListOfLines],
    header_text: ListOfLines = "Add a new volunteer",
    volunteer_and_text: VolunteerAndVerificationText = default_volunteer_and_text,
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
        verify_text = verify_volunteer_and_warn(volunteer)
    except Exception as e:
        volunteer = copy(default)
        verify_text = (
            "Doesn't appear to be a valid cadet (wrong date time in old browser?) error code %s"
            % str(e)
        )

    return VolunteerAndVerificationText(volunteer=volunteer, verification_text=verify_text)


def get_volunteer_from_form(interface: abstractInterface) -> Volunteer:
    first_name = interface.value_from_form(FIRST_NAME).strip().title()
    surname = interface.value_from_form(SURNAME).strip().title()

    return Volunteer(first_name=first_name, surname=surname)


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
        "Added volunteer %s" % str(volunteer), interface=interface
    )


def add_volunteer_from_form_to_data(interface) -> Volunteer:
    volunteer = get_volunteer_from_form(interface)
    add_new_verified_volunteer(volunteer)

    return volunteer


def get_footer_buttons_for_add_volunteer_form(form_is_empty: bool) -> Line:
    final_submit = Button(FINAL_ADD_BUTTON_LABEL)
    check_submit = Button(CHECK_BUTTON_LABEL)
    if form_is_empty:
        return Line([cancel_button, check_submit])
    else:
        return Line([cancel_button, check_submit, final_submit])



def verify_volunteer_and_warn(volunteer: Volunteer) -> str:
    warn_text = ""
    if len(volunteer.surname) < 4:
        warn_text += "Surname seems too short. "
    if len(volunteer.first_name) < 4:
        warn_text += "First name seems too short. "
    warn_text += warning_for_similar_volunteers(volunteer)

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text


def warning_for_similar_volunteers(volunteer: Volunteer) -> str:
    similar_volunteers = list_of_similar_volunteers(volunteer)

    if len(similar_volunteers) > 0:
        similar_volunteers_str = ", ".join(
            [str(other_volunteer) for other_volunteer in similar_volunteers]
        )
        ## Some similar cadets, let's see if it's a match
        return "Following existing volunteers look awfully similar:\n %s" % similar_volunteers_str
    else:
        return ""


def list_of_similar_volunteers(volunteer: Volunteer) -> list:
    existing_volunteers = data.data_list_of_volunteers.read()
    similar_volunteers = existing_volunteers.similar_volunteers(
        volunteer=volunteer
    )

    return similar_volunteers


def add_new_verified_volunteer(volunteer: Volunteer):
    data.data_list_of_volunteers.add(volunteer)

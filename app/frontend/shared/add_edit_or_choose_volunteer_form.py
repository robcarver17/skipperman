from copy import copy
from dataclasses import dataclass
from typing import Union

from app.backend.volunteers.skills import (
    get_dict_of_existing_skills_for_volunteer,
    save_skills_for_volunteer,
)
from app.frontend.forms.form_utils import (
    get_dict_of_skills_from_form,
    checked_and_labels_dict_for_skills_form,
)

from app.backend.volunteers.add_edit_volunteer import (
    add_new_verified_volunteer,
    verify_volunteer_and_warn,
)

from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    cancel_menu_button,
    Button, HelpButton,
)
from app.objects.abstract_objects.abstract_form import Form, textInput, checkboxInput, dropDownInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_text import bold
from app.objects.utilities.exceptions import arg_not_passed, MISSING_FROM_FORM
from app.objects.volunteers import Volunteer, default_volunteer


def get_volunteer_from_form(interface: abstractInterface) -> Volunteer:
    first_name = interface.value_from_form(FIRST_NAME)
    surname = interface.value_from_form(SURNAME)

    return Volunteer.new(first_name=first_name, surname=surname)


def add_volunteer_from_form_to_data(interface) -> Volunteer:
    volunteer = get_volunteer_from_form(interface)
    add_new_verified_volunteer(volunteer=volunteer, object_store=interface.object_store)
    interface.flush_cache_to_store()

    return volunteer


@dataclass
class VolunteerAndVerificationText:
    volunteer: Volunteer
    verification_text: str = ""

    @property
    def is_default(self) -> bool:
        return self.volunteer is default_volunteer


def verify_form_with_volunteer_details(
    interface: abstractInterface, default=default_volunteer
) -> VolunteerAndVerificationText:
    try:
        volunteer = get_volunteer_from_form(interface)
        verify_text = verify_volunteer_and_warn(
            object_store=interface.object_store, volunteer=volunteer
        )
    except Exception as e:
        volunteer = copy(default)
        verify_text = "Doesn't appear to be a valid volunteer error code %s" % str(e)

    return VolunteerAndVerificationText(
        volunteer=volunteer, verification_text=verify_text
    )


default_volunteer_and_text = VolunteerAndVerificationText(
    volunteer=default_volunteer, verification_text=""
)


def get_add_volunteer_form_with_information_passed(
    footer_buttons: Union[Line, ListOfLines, ButtonBar],
    header_text: ListOfLines = "Add a new volunteer",
    help_string: str = arg_not_passed,
    volunteer_and_text: VolunteerAndVerificationText = default_volunteer_and_text,  ## if blank
        availability_checkbox: bool = False
) -> Form:
    form_fields = form_fields_for_add_volunteer(volunteer_and_text.volunteer, availability_checkbox=availability_checkbox)
    if help_string is arg_not_passed:
        nav_bar = ''
    else:
        nav_bar = ButtonBar([HelpButton(help_string)])

    list_of_lines_inside_form = ListOfLines(
        [
            nav_bar,
            _______________,
            header_text,
            _______________,
            form_fields,
            _______________,
            bold(volunteer_and_text.verification_text),
            _______________,
            footer_buttons,
        ]
    )

    return Form(list_of_lines_inside_form)


def form_fields_for_add_volunteer(volunteer: Volunteer, availability_checkbox: bool = False):
    first_name = textInput(
        input_label="First name", input_name=FIRST_NAME, value=volunteer.first_name
    )
    surname = textInput(
        input_label="Second name", input_name=SURNAME, value=volunteer.surname
    )
    form_fields = [first_name, surname]
    if availability_checkbox:
        form_fields.append(dropDownInput(
            dict_of_options={VOLUNTEERING:VOLUNTEERING, NO_AVAILABILITY:NO_AVAILABILITY},
            input_label="Select if parent on site ",
            input_name=NO_AVAILABILITY_NAME,
            default_label=VOLUNTEERING
        ))

    form_fields = ListOfLines(form_fields).add_Lines()

    return form_fields

NO_AVAILABILITY="Parent on site, not volunteering"
VOLUNTEERING = "Helping"
NO_AVAILABILITY_NAME="availability_checkbox_nmae"

def availability_in_form_set_to_no(interface: abstractInterface):
    value = interface.value_from_form(NO_AVAILABILITY_NAME, default='')
    return value == NO_AVAILABILITY

def get_footer_buttons_for_add_volunteer_form(form_is_empty: bool) -> ButtonBar:
    if form_is_empty:
        return ButtonBar([cancel_menu_button, check_submit_button])
    else:
        return ButtonBar([cancel_menu_button, check_submit_button, final_submit_button])


def get_and_save_volunteer_skills_from_form(
    interface: abstractInterface, volunteer: Volunteer
):
    dict_of_skills = get_dict_of_skills_from_form(
        interface=interface, field_name=SKILLS
    )
    if dict_of_skills is MISSING_FROM_FORM:
        print("skills dict not in form")
        return

    save_skills_for_volunteer(
        object_store=interface.object_store,
        volunteer=volunteer,
        dict_of_skills=dict_of_skills,
    )


def skills_form_entries(interface: abstractInterface, volunteer: Volunteer):
    skills_dict = get_dict_of_existing_skills_for_volunteer(
        object_store=interface.object_store, volunteer=volunteer
    )
    skills_dict_checked, dict_of_labels = checked_and_labels_dict_for_skills_form(
        skills_dict
    )

    return checkboxInput(
        input_label="Volunteer skills:",
        dict_of_checked=skills_dict_checked,
        dict_of_labels=dict_of_labels,
        input_name=SKILLS,
    )


SKILLS = "skills"
FIRST_NAME = "first_name"
SURNAME = "surname"


CHECK_BUTTON_LABEL = "Check details entered"
FINAL_ADD_BUTTON_LABEL = "Yes - these details are correct - add this volunteer"

final_submit_button = Button(FINAL_ADD_BUTTON_LABEL, nav_button=True)
check_submit_button = Button(CHECK_BUTTON_LABEL, nav_button=True)

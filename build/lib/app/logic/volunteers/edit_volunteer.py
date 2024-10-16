from typing import Union

from app.frontend.forms.form_utils import checked_and_labels_dict_for_skills_form, get_dict_of_skills_from_form
from app.data_access.configuration.configuration import WEBLINK_FOR_QUALIFICATIONS

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    textInput,
    checkboxInput,
    Link,
)
from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    cancel_menu_button,
    save_menu_button,
)
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.frontend.form_handler import (
    initial_state_form,
    button_error_and_back_to_initial_state_form,
)
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.OLD_backend.volunteers.volunteers import (
    update_existing_volunteer, get_dict_of_existing_skills,
)
from app.backend.volunteers.skills import save_skills_for_volunteer
from app.frontend.shared.volunteer_state import get_volunteer_from_state
from app.frontend.shared.add_edit_volunteer_forms import get_volunteer_from_form
from app.objects.volunteers import Volunteer


def display_form_edit_individual_volunteer(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    try:
        volunteer = get_volunteer_from_state(interface)
    except:
        interface.log_error(
            "Volunteer selected no longer in list- someone else has deleted or file corruption?"
        )
        return initial_state_form

    form = form_to_edit_individual_volunteer(interface=interface, volunteer=volunteer)

    return form


def form_to_edit_individual_volunteer(
    interface: abstractInterface,
    volunteer: Volunteer,
) -> Form:
    core_entries = core_volunteer_form_entries(volunteer)
    skills_entries = skills_form_entries(interface=interface, volunteer=volunteer)
    link = Link(
        url=WEBLINK_FOR_QUALIFICATIONS,
        string="See qualifications_and_ticks table",
        open_new_window=True,
    )

    footer_buttons = ButtonBar([cancel_menu_button, save_menu_button])

    return Form(
        [
            ListOfLines(
                [
                    "Edit volunteer:",
                    _______________,
                    core_entries,
                    _______________,
                    skills_entries,
                    link,
                    _______________,
                    _______________,
                    footer_buttons,
                ]
            )
        ]
    )


def core_volunteer_form_entries(volunteer: Volunteer) -> ListOfLines:
    first_name = textInput(
        input_label="First name", input_name=FIRST_NAME, value=volunteer.first_name
    )
    surname = textInput(
        input_label="Second name", input_name=SURNAME, value=volunteer.surname
    )

    return ListOfLines([Line(first_name), Line(surname)])


def skills_form_entries(interface: abstractInterface, volunteer: Volunteer):
    skills_dict = get_dict_of_existing_skills(
        data_layer=interface.data, volunteer=volunteer
    )
    skills_dict_checked, dict_of_labels = checked_and_labels_dict_for_skills_form(skills_dict)

    return checkboxInput(
        input_label="Volunteer skills:",
        dict_of_checked=skills_dict_checked,
        dict_of_labels=dict_of_labels,
        input_name=SKILLS,
    )


def post_form_edit_individual_volunteer(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    previous_page_form = interface.get_new_display_form_for_parent_of_function(
        display_form_edit_individual_volunteer
    )

    if cancel_menu_button.pressed(button):
        return previous_page_form
    elif save_menu_button.pressed(button):
        modify_volunteer_given_form_contents(interface=interface)
        interface.flush_cache_to_store()
        return previous_page_form
    else:
        return button_error_and_back_to_initial_state_form(interface)


def modify_volunteer_given_form_contents(interface: abstractInterface):
    original_volunteer = get_volunteer_from_state(interface)

    get_and_save_core_volunteer_details_from_form(
        interface=interface, original_volunteer=original_volunteer
    )
    get_and_save_volunteer_skills_from_form(
        interface=interface, volunteer=original_volunteer
    )


def get_and_save_core_volunteer_details_from_form(
    interface: abstractInterface, original_volunteer: Volunteer
):
    volunteer_details_from_form = get_volunteer_from_form(interface)
    volunteer_details_from_form.id = original_volunteer.id  ## won't be in form
    update_existing_volunteer(
        data_layer=interface.data, volunteer=volunteer_details_from_form
    )


def get_and_save_volunteer_skills_from_form(
    interface: abstractInterface, volunteer: Volunteer
):
    dict_of_skills = get_dict_of_skills_from_form(
        interface=interface,
        field_name=SKILLS
    )
    save_skills_for_volunteer(
        data_layer=interface.data, volunteer=volunteer, dict_of_skills=dict_of_skills
    )



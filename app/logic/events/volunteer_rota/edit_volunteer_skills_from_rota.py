from typing import Union

from app.data_access.configuration.configuration import WEBLINK_FOR_QUALIFICATIONS

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.volunteers.constants import CANCEL_BUTTON_LABEL, SAVE_BUTTON_LABEL

from app.logic.volunteers.edit_volunteer import get_and_save_volunteer_skills_from_form,  skills_form_entries
from app.logic.volunteers.volunteer_state import get_volunteer_from_state

from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import Form, NewForm, Link
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.objects.volunteers import Volunteer


def display_form_edit_individual_volunteer_skills_from_rota(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    volunteer = get_volunteer_from_state(interface)
    skills_entries = skills_form_entries(interface=interface, volunteer=volunteer)
    link = Link(url=WEBLINK_FOR_QUALIFICATIONS, string="See qualifications table", open_new_window=True)

    footer_buttons = Line([Button(CANCEL_BUTTON_LABEL), Button(SAVE_BUTTON_LABEL)])

    return Form([
        ListOfLines([
            "Edit volunteer %s skills:" % volunteer.name,
            _______________,
            skills_entries,
            _______________,
            link,
            _______________,
            footer_buttons
        ])
    ])


def post_form_edit_individual_volunteer_skills_from_rota(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    if button==CANCEL_BUTTON_LABEL:
        pass
    elif button==SAVE_BUTTON_LABEL:
        modify_volunteer_from_rota_given_form_contents(interface=interface)
    else:
        raise Exception("Button %s not recognised" % button)

    interface._DONT_CALL_DIRECTLY_USE_FLUSH_save_stored_items()

    return previous_form(interface)


def modify_volunteer_from_rota_given_form_contents(interface: abstractInterface):
    volunteer = get_volunteer_from_state(interface)

    get_and_save_volunteer_skills_from_form(interface=interface, volunteer=volunteer)

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_edit_individual_volunteer_skills_from_rota)

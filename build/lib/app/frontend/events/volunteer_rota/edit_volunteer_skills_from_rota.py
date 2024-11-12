from typing import Union

from app.data_access.configuration.configuration import WEBLINK_FOR_QUALIFICATIONS

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.frontend.shared.add_edit_volunteer_forms import (
    get_and_save_volunteer_skills_from_form,
    skills_form_entries,
)
from app.frontend.shared.volunteer_state import get_volunteer_from_state

from app.objects.abstract_objects.abstract_buttons import (
    Button,
    SAVE_BUTTON_LABEL,
    CANCEL_BUTTON_LABEL,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm, Link
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)


def display_form_edit_individual_volunteer_skills_from_rota(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    volunteer = get_volunteer_from_state(interface)
    skills_entries = skills_form_entries(interface=interface, volunteer=volunteer)
    link = Link(
        url=WEBLINK_FOR_QUALIFICATIONS,
        string="See qualifications_and_ticks table",
        open_new_window=True,
    )

    footer_buttons = Line([cancel_button, save_button])

    return Form(
        [
            ListOfLines(
                [
                    "Edit volunteer %s skills:" % volunteer.name,
                    _______________,
                    skills_entries,
                    _______________,
                    link,
                    _______________,
                    footer_buttons,
                ]
            )
        ]
    )


save_button = Button(SAVE_BUTTON_LABEL)
cancel_button = Button(CANCEL_BUTTON_LABEL)


def post_form_edit_individual_volunteer_skills_from_rota(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    if cancel_button.pressed(button):
        pass
    elif save_button.pressed(button):
        modify_volunteer_from_rota_given_form_contents(interface=interface)
    else:
        raise Exception("Button %s not recognised" % button)

    interface.flush_cache_to_store()

    return previous_form(interface)


def modify_volunteer_from_rota_given_form_contents(interface: abstractInterface):
    volunteer = get_volunteer_from_state(interface)

    get_and_save_volunteer_skills_from_form(interface=interface, volunteer=volunteer)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_edit_individual_volunteer_skills_from_rota
    )

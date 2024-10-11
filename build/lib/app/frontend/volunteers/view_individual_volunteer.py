from typing import Union

#from app.OLD_backend.rota.volunteer_history import get_all_roles_across_recent_events_for_volunteer_as_dict_latest_first
from app.backend.volunteers.skills import get_dict_of_existing_skills_for_volunteer
from app.frontend.volunteers.edit_cadet_connections import (
    display_form_edit_cadet_volunteer_connections,
)
from app.frontend.volunteers.edit_volunteer import display_form_edit_individual_volunteer
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    back_menu_button, HelpButton,
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
from app.backend.volunteers.connected_cadets import get_list_of_cadets_associated_with_volunteer
from app.frontend.shared.volunteer_state import get_volunteer_from_state

from app.objects.volunteers import Volunteer


def display_form_view_individual_volunteer(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    try:
        volunteer = get_volunteer_from_state(interface)
    except:
        interface.log_error(
            "Volunteer selected no longer in list- someone else has deleted or file corruption?"
        )
        return initial_state_form

    return display_form_for_selected_volunteer(volunteer=volunteer, interface=interface)


def display_form_for_selected_volunteer(
    volunteer: Volunteer, interface: abstractInterface
) -> Form:
    lines_of_allocations = list_of_lines_with_allocations_and_roles(
        interface=interface, volunteer=volunteer
    )

    connected = lines_for_connected_cadets(interface=interface, volunteer=volunteer)
    skills = list_of_skills_as_list_of_lines(interface=interface, volunteer=volunteer)
    buttons = buttons_for_volunteer_form()
    return Form(
        ListOfLines(
            [
                buttons,
                _______________,
                str(volunteer),
                _______________,
                lines_of_allocations,
                _______________,
                skills,
                _______________,
                connected,

            ]
        )
    )



def list_of_lines_with_allocations_and_roles(
    interface: abstractInterface, volunteer: Volunteer
) -> ListOfLines:
 #   dict_of_roles = get_all_roles_across_recent_events_for_volunteer_as_dict_latest_first(
 #       data_layer=interface.data, volunteer=volunteer
 #   )

 #   return from_dict_of_roles_to_list_of_lines(dict_of_roles)

    return ListOfLines(["no group data"])

def from_dict_of_roles_to_list_of_lines(dict_of_roles: dict) -> ListOfLines:
    if len(dict_of_roles) == 0:
        return ListOfLines([])

    return ListOfLines(
        ["Events helping at:", _______________]
        + ["%s: %s" % (str(event), role) for event, role in dict_of_roles.items()]
    ).add_Lines()


def list_of_skills_as_list_of_lines(
    interface: abstractInterface, volunteer: Volunteer
) -> ListOfLines:

    skills = get_dict_of_existing_skills_for_volunteer(object_store=interface.object_store, volunteer=volunteer)
    skills_held = skills.skills_held_as_str()
    skills_not_held = skills.skills_not_held_as_str()

    return ListOfLines(
        [
            Line("Skills held: %s" % skills_held),
            Line("Skills missing: %s" % skills_not_held)
        ]
    )


def lines_for_connected_cadets(
    interface: abstractInterface, volunteer: Volunteer
) -> Line:
    cadets = get_list_of_cadets_associated_with_volunteer(object_store=interface.object_store, volunteer=volunteer)
    if len(cadets) == 0:
        return Line([])
    cadets_as_str = cadets.as_str()
    return Line("Connected to: %s" % cadets_as_str)


def buttons_for_volunteer_form() -> ButtonBar:
    return ButtonBar(
        [

            back_menu_button,
            main_edit_button,
           connection_edit_button,
            help_button,
        ]
    )



EDIT_BUTTON_LABEL = "Edit volunteer name and skills"
EDIT_CADET_CONNECTIONS_BUTTON_LABEL = "Edit connection with sailors"

main_edit_button = Button(EDIT_BUTTON_LABEL, nav_button=True)
connection_edit_button =  Button(EDIT_CADET_CONNECTIONS_BUTTON_LABEL, nav_button=True)
help_button = HelpButton("view_individual_volunteer_help")

def post_form_view_individual_volunteer(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    if back_menu_button.pressed(button):
        return previous_form(interface)
    elif main_edit_button.pressed(button):
        return edit_volunteer_form(interface)
    elif connection_edit_button.pressed(button):
        return edit_connections_form(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)


def previous_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_form_view_individual_volunteer
    )




def edit_volunteer_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_form_given_function(display_form_edit_individual_volunteer)


def edit_connections_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_form_given_function(
        display_form_edit_cadet_volunteer_connections
    )

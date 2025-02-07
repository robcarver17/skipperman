from typing import Union

from app.backend.groups.cadets_with_groups_at_event import (
    get_list_of_groups_at_event_given_list_of_cadets,
)
from app.backend.volunteers.connected_cadets import (
    get_list_of_cadets_associated_with_volunteer,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.objects.events import Event

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_list_of_active_cadets_at_event,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.frontend.shared.events_state import get_event_from_state

from app.frontend.volunteers.edit_cadet_connections import (
    get_cadet_from_button_pressed,
)
from app.frontend.shared.cadet_connection_forms import (
    form_to_edit_connections,
    get_list_of_delete_cadet_buttons_given_connected_cadets,
    add_connection_button,
    get_selected_cadet_from_form,
)
from app.frontend.shared.volunteer_state import (
    get_volunteer_from_state,
)

from app.objects.cadets import ListOfCadets

from app.objects.abstract_objects.abstract_buttons import back_menu_button
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.exceptions import CadetNotSelected
from app.backend.volunteers.connected_cadets import (
    add_volunteer_connection_to_cadet_in_master_list_of_volunteers,
)

from app.backend.volunteers.connected_cadets import delete_cadet_connection


def display_form_edit_cadet_connections_from_rota(interface: abstractInterface):
    event = get_event_from_state(interface)
    volunteer = get_volunteer_from_state(interface)
    connected_cadets = get_list_of_cadets_associated_with_volunteer(
        object_store=interface.object_store, volunteer=volunteer
    )
    group_text = get_group_text(
        interface=interface, event=event, connected_cadets=connected_cadets
    )
    instruction_line = Line(
        [
            "Following are connected cadets for volunteer %s at event %s - add or modify if required"
            % (volunteer.name, str(event))
        ]
    )

    header_text = ListOfLines([instruction_line, group_text])

    list_of_cadets_at_event = get_list_of_active_cadets_at_event(
        object_store=interface.object_store,
        event=event,
    )

    form = form_to_edit_connections(volunteer=volunteer, existing_connected_cadets=connected_cadets,
                                    header_text=header_text, list_of_cadets_to_choose_from=list_of_cadets_at_event)

    return form


def get_group_text(
    interface: abstractInterface, event: Event, connected_cadets: ListOfCadets
) -> Line:
    groups = get_list_of_groups_at_event_given_list_of_cadets(
        object_store=interface.object_store,
        event=event,
        list_of_cadets=connected_cadets,
    )
    text_of_groups = ", ".join([group.name for group in groups])

    if len(text_of_groups) == 0:
        return Line([""])

    return Line(["Connected cadets are in following groups: %s" % text_of_groups])


def post_form_edit_cadet_connections_from_rota(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    button = interface.last_button_pressed()

    ### Buttons are back; delete button for individual cadet connection; add to add a new connection
    if back_menu_button.pressed(last_button=button):
        return previous_form(interface)

    elif add_connection_button.pressed(button):
        add_cadet_connection_from_form(interface)
        interface.flush_cache_to_store()
        return display_form_edit_cadet_connections_from_rota(interface)
    elif last_button_pressed_was_delete_cadet_connection(interface):
        delete_event_connection_given_form(interface=interface)
        interface.flush_cache_to_store()
        return display_form_edit_cadet_connections_from_rota(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)


def last_button_pressed_was_delete_cadet_connection(interface: abstractInterface):
    return (
        interface.last_button_pressed()
        in get_list_of_delete_cadet_buttons_with_currently_connected_cadets(interface)
    )


def get_list_of_delete_cadet_buttons_with_currently_connected_cadets(
    interface: abstractInterface,
):
    volunteer = get_volunteer_from_state(interface)
    connected_cadets = get_list_of_cadets_associated_with_volunteer(
        object_store=interface.object_store, volunteer=volunteer
    )
    list_of_delete_cadet_buttons = (
        get_list_of_delete_cadet_buttons_given_connected_cadets(connected_cadets)
    )

    return list_of_delete_cadet_buttons


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_edit_cadet_connections_from_rota
    )


def delete_event_connection_given_form(interface: abstractInterface):
    cadet = get_cadet_from_button_pressed(interface)
    volunteer = get_volunteer_from_state(interface)

    delete_cadet_connection(
        object_store=interface.object_store, cadet=cadet, volunteer=volunteer
    )


def add_cadet_connection_from_form(interface: abstractInterface):
    try:
        selected_cadet = get_selected_cadet_from_form(interface)
    except CadetNotSelected:
        interface.log_error(
            "You have to select a cadet from the dropdown before adding"
        )
        return
    volunteer = get_volunteer_from_state(interface)
    add_volunteer_connection_to_cadet_in_master_list_of_volunteers(
        object_store=interface.object_store,
        volunteer=volunteer,
        cadet=selected_cadet,
    )

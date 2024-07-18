from typing import Union

from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form

from app.OLD_backend.volunteers.volunteer_allocation import get_list_of_connected_cadets_given_volunteer_at_event, \
    remove_volunteer_and_cadet_association_at_event, add_volunteer_and_cadet_association_for_existing_volunteer
from app.objects.events import Event

from app.OLD_backend.group_allocations.cadet_event_allocations import (
    get_list_of_groups_at_event_given_list_of_cadets,
    get_list_of_active_cadets_at_event,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.logic.shared.events_state import get_event_from_state

from app.logic.volunteers.edit_cadet_connections import (
    get_cadet_from_button_pressed,
)
from app.logic.shared.cadet_connection_forms import form_to_edit_connections,  \
    get_list_of_delete_cadet_buttons_given_connected_cadets, add_connection_button, \
     get_selected_cadet_from_form
from app.logic.shared.volunteer_state import  get_volunteer_from_state, \
    get_volunteer_at_event_with_id_from_state

from app.objects.cadets import ListOfCadets

from app.objects.abstract_objects.abstract_buttons import back_menu_button, Button
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.exceptions import CadetNotSelected


def display_form_edit_cadet_connections_from_rota(interface: abstractInterface):
    event = get_event_from_state(interface)
    volunteer = get_volunteer_from_state(interface)
    connected_cadets = get_list_of_connected_cadets(interface)
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
        data_layer=interface.data,
        event=event,
    )

    form = form_to_edit_connections(
        volunteer=volunteer,
        connected_cadets=connected_cadets,
        from_list_of_cadets=list_of_cadets_at_event,
        header_text=header_text,
    )

    return form


def get_list_of_connected_cadets(interface: abstractInterface) -> ListOfCadets:
    volunteer_at_event = get_volunteer_at_event_with_id_from_state(interface)
    connected_cadets = get_list_of_connected_cadets_given_volunteer_at_event(data_layer=interface.data, volunteer_at_event=volunteer_at_event)

    return connected_cadets


def get_group_text(
    interface: abstractInterface, event: Event, connected_cadets: ListOfCadets
) -> Line:
    groups = get_list_of_groups_at_event_given_list_of_cadets(
        data_layer=interface.data, event=event, list_of_cadets=connected_cadets
    )
    text_of_groups = ", ".join([group.group_name for group in groups])

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
        add_event_specific_cadet_connection_from_form(interface)

    elif last_button_pressed_was_delete_cadet_connection(interface):
        delete_event_connection_given_form(interface=interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()

    return display_form_edit_cadet_connections_from_rota(interface)

def last_button_pressed_was_delete_cadet_connection(interface: abstractInterface):
    return interface.last_button_pressed() in get_list_of_delete_cadet_buttons_with_currently_connected_cadets(interface)

def get_list_of_delete_cadet_buttons_with_currently_connected_cadets(
    interface: abstractInterface,
):
    connected_cadets = get_list_of_connected_cadets(interface)
    list_of_delete_cadet_buttons = get_list_of_delete_cadet_buttons_given_connected_cadets(connected_cadets)

    return list_of_delete_cadet_buttons


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_edit_cadet_connections_from_rota
    )


def delete_event_connection_given_form(interface: abstractInterface):
    cadet = get_cadet_from_button_pressed(interface)
    volunteer= get_volunteer_from_state(interface)
    event = get_event_from_state(interface)

    remove_volunteer_and_cadet_association_at_event(
        data_layer=interface.data, cadet=cadet, volunteer=volunteer, event=event
    )


def add_event_specific_cadet_connection_from_form(interface: abstractInterface):
    try:
        selected_cadet = get_selected_cadet_from_form(interface)
    except CadetNotSelected:
        interface.log_error(
            "You have to select a cadet from the dropdown before adding"
        )
        return
    volunteer = get_volunteer_from_state(interface)
    event = get_event_from_state(interface)
    add_volunteer_and_cadet_association_for_existing_volunteer(
        data_layer=interface.data,
        event=event,
        volunteer=volunteer,
        cadet=selected_cadet
    )


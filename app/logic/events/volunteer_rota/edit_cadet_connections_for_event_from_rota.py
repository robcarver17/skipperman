from typing import Union

from app.objects.events import Event

from app.backend.group_allocations.cadet_event_allocations import (
    get_list_of_groups_at_event_given_list_of_cadets,
    get_list_of_active_cadets_at_event,
)
from app.backend.volunteers.volunteers import get_volunteer_from_id
from app.backend.volunteers.volunteer_rota import (
    remove_volunteer_and_cadet_association_at_event,
    add_volunteer_and_cadet_association_for_existing_volunteer,
    get_volunteer_at_event,
)

from app.backend.cadets import DEPRECATE_cadet_from_id_USE_get_cadet_from_id

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.logic.events.events_in_state import get_event_from_state

from app.logic.volunteers.constants import (
    BACK_BUTTON_LABEL,
    ADD_CONNECTION_BUTTON_LABEL,
    CONNECTION,
)
from app.logic.volunteers.edit_cadet_connections import (
    form_to_edit_connections,
    get_list_of_delete_cadet_buttons,
    get_cadet_connection_to_delete_from_form,
    CADET_FILLER,
)
from app.logic.volunteers.volunteer_state import get_volunteer_id_selected_from_state

from app.objects.cadets import ListOfCadets

from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line


def display_form_edit_cadet_connections_from_rota(interface: abstractInterface):
    volunteer_id = get_volunteer_id_selected_from_state(interface)  ## NEEDS TO BE SET
    event = get_event_from_state(interface)
    volunteer = get_volunteer_from_id(interface, volunteer_id)
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
        event=event, interface=interface
    )

    form = form_to_edit_connections(
        volunteer=volunteer,
        connected_cadets=connected_cadets,
        from_list_of_cadets=list_of_cadets_at_event,
        text=header_text,
    )

    return form


def get_list_of_connected_cadets(interface: abstractInterface) -> ListOfCadets:
    volunteer_id = get_volunteer_id_selected_from_state(interface)  ## NEEDS TO BE SET
    event = get_event_from_state(interface)
    volunteer_at_event = get_volunteer_at_event(
        interface=interface, volunteer_id=volunteer_id, event=event
    )
    cadet_ids = volunteer_at_event.list_of_associated_cadet_id

    connected_cadets = ListOfCadets(
        [
            DEPRECATE_cadet_from_id_USE_get_cadet_from_id(
                interface=interface, cadet_id=cadet_id
            )
            for cadet_id in cadet_ids
        ]
    )

    return connected_cadets


def get_group_text(
    interface: abstractInterface, event: Event, connected_cadets: ListOfCadets
) -> Line:
    groups = get_list_of_groups_at_event_given_list_of_cadets(
        interface=interface, event=event, list_of_cadets=connected_cadets
    )
    text_of_groups = ", ".join([group.group_name for group in groups])

    if len(text_of_groups) == 0:
        return ""

    return Line(["Connected cadets are in following groups: %s" % text_of_groups])


def post_form_edit_cadet_connections_from_rota(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    button = interface.last_button_pressed()

    list_of_delete_cadet_buttons = (
        get_list_of_delete_cadet_buttons_with_connected_cadets(interface)
    )

    ### Buttons are back; delete button for individual cadet connection; add to add a new connection
    if button == BACK_BUTTON_LABEL:
        return previous_form(interface)
    elif button == ADD_CONNECTION_BUTTON_LABEL:
        add_event_specific_cadet_connection_from_form(interface)
    elif button in list_of_delete_cadet_buttons:
        delete_event_connection_given_form(interface=interface)
    else:
        raise Exception("Weirdly named button %s pressed" % button)

    interface._DONT_CALL_DIRECTLY_USE_FLUSH_save_stored_items()

    return display_form_edit_cadet_connections_from_rota(interface)


def get_list_of_delete_cadet_buttons_with_connected_cadets(
    interface: abstractInterface,
):
    connected_cadets = get_list_of_connected_cadets(interface)
    list_of_delete_cadet_buttons = get_list_of_delete_cadet_buttons(connected_cadets)

    return list_of_delete_cadet_buttons


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_edit_cadet_connections_from_rota
    )


def delete_event_connection_given_form(interface: abstractInterface):
    cadet = get_cadet_connection_to_delete_from_form(interface)
    volunteer_id = get_volunteer_id_selected_from_state(interface)
    event = get_event_from_state(interface)
    print("Remove %s %s %s" % (cadet.id, volunteer_id, str(event)))
    remove_volunteer_and_cadet_association_at_event(
        interface=interface, cadet_id=cadet.id, volunteer_id=volunteer_id, event=event
    )


def add_event_specific_cadet_connection_from_form(interface: abstractInterface):
    selected_cadet_id = interface.value_from_form(CONNECTION)
    if selected_cadet_id == CADET_FILLER:
        interface.log_error(
            "You have to select a cadet from the dropdown before adding"
        )
        return
    volunteer_id = get_volunteer_id_selected_from_state(interface)
    selected_cadet = DEPRECATE_cadet_from_id_USE_get_cadet_from_id(
        interface=interface, cadet_id=selected_cadet_id
    )
    event = get_event_from_state(interface)
    add_volunteer_and_cadet_association_for_existing_volunteer(
        interface=interface,
        volunteer_id=volunteer_id,
        cadet_id=selected_cadet.id,
        event=event,
    )

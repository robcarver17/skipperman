from typing import Union, List
from app.backend.cadets.list_of_cadets import get_list_of_cadets_sorted_by_surname
from app.frontend.shared.cadet_connection_forms import (
    form_to_edit_connections,
    add_connection_button,
    get_list_of_delete_cadet_buttons_given_connected_cadets,
    get_cadet_from_button_pressed,
    get_selected_cadet_from_form,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import (
    back_menu_button,
    Button,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
)
from app.frontend.form_handler import (
    initial_state_form,
    button_error_and_back_to_initial_state_form,
)
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

from app.backend.volunteers.connected_cadets import (
    get_list_of_cadets_associated_with_volunteer,
    delete_cadet_connection,
    add_volunteer_connection_to_cadet_in_master_list_of_volunteers,
)

from app.frontend.shared.volunteer_state import get_volunteer_from_state
from app.objects.utilities.exceptions import CadetNotSelected, MissingData


def display_form_edit_cadet_volunteer_connections(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    try:
        volunteer = get_volunteer_from_state(interface)
    except:
        interface.log_error(
            "Volunteer selected no longer in list- someone else has deleted or file corruption?"
        )
        return initial_state_form

    connected_cadets = get_list_of_cadets_associated_with_volunteer(
        object_store=interface.object_store, volunteer=volunteer
    )
    from_list_of_cadets = get_list_of_cadets_sorted_by_surname(
        object_store=interface.object_store
    )

    form = form_to_edit_connections(
        volunteer=volunteer,
        existing_connected_cadets=connected_cadets,
        header_text=header_text,
        list_of_cadets_to_choose_from=from_list_of_cadets,
    )

    return form


header_text = ListOfLines(
    [
        "Edit volunteer and sailors connections (used to avoid putting group_allocations/parents together and to find volunteers):"
    ]
)


def post_form_edit_cadet_volunteer_connections(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    button = interface.last_button_pressed()
    ### Buttons are back; delete button for individual cadet connection; add to add a new connection
    if back_menu_button.pressed(button):
        return previous_form(interface)

    elif add_connection_button.pressed(button):
        add_connection_from_form(interface)
        ## might want to do more, display form again
        return display_form_edit_cadet_volunteer_connections(interface)

    else:
        ## must be delete button
        return post_form_edit_cadet_volunteer_connections_when_delete_button_probably_pressed(
            interface
        )


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_edit_cadet_volunteer_connections
    )


def post_form_edit_cadet_volunteer_connections_when_delete_button_probably_pressed(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    if last_button_pressed_was_delete_cadet_button(interface=interface):
        delete_connection_given_form(interface=interface)
        ## might want to do more
        return display_form_edit_cadet_volunteer_connections(interface)
    else:
        ## not a delete button
        return button_error_and_back_to_initial_state_form(interface)


def last_button_pressed_was_delete_cadet_button(interface: abstractInterface) -> bool:
    button = interface.last_button_pressed()
    list_of_delete_cadet_buttons = get_list_of_delete_cadet_buttons(interface)
    for button_name in list_of_delete_cadet_buttons:
        if Button(button_name).pressed(button):
            return True

    return False


def get_list_of_delete_cadet_buttons(interface: abstractInterface) -> List[str]:
    volunteer = get_volunteer_from_state(interface)
    connected_cadets = get_list_of_cadets_associated_with_volunteer(
        object_store=interface.object_store, volunteer=volunteer
    )

    list_of_delete_cadet_buttons = (
        get_list_of_delete_cadet_buttons_given_connected_cadets(connected_cadets)
    )

    return list_of_delete_cadet_buttons


def add_connection_from_form(interface: abstractInterface):
    try:
        selected_cadet = get_selected_cadet_from_form(interface)
    except CadetNotSelected:
        interface.log_error(
            "You have to select a cadet from the dropdown before adding"
        )
        return
    except MissingData:
        interface.log_error("Cadet missing from form")
        return

    volunteer = get_volunteer_from_state(interface)

    
    add_volunteer_connection_to_cadet_in_master_list_of_volunteers(
        object_store=interface.object_store, cadet=selected_cadet, volunteer=volunteer
    )
    interface.DEPRECATE_flush_and_clear()


def delete_connection_given_form(interface: abstractInterface):
    cadet = get_cadet_from_button_pressed(interface)
    volunteer = get_volunteer_from_state(interface)

    
    delete_cadet_connection(
        object_store=interface.object_store, cadet=cadet, volunteer=volunteer
    )
    interface.DEPRECATE_flush_and_clear()

from typing import Union, List

from app.backend.cadets import (
    get_sorted_list_of_cadets,
    get_list_of_cadets_similar_to_name_first,
    DEPRECATE_cadet_from_id_USE_get_cadet_from_id,
    DEPRECATE_get_cadet_given_cadet_as_str,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm, dropDownInput
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    cancel_menu_button,
    back_menu_button,
)
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.logic.abstract_logic_api import (
    initial_state_form,
    button_error_and_back_to_initial_state_form,
)
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.logic.volunteers.constants import *
from app.backend.volunteers.volunteers import (
    DEPRECATE_get_connected_cadets,
    delete_connection_in_data,
    add_volunteer_connection_to_cadet_in_master_list_of_volunteers,
)
from app.backend.data.volunteers import SORT_BY_SURNAME
from app.logic.volunteers.volunteer_state import get_volunteer_from_state
from app.objects.volunteers import Volunteer
from app.objects.cadets import Cadet, ListOfCadets


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
    connected_cadets = DEPRECATE_get_connected_cadets(
        interface=interface, volunteer=volunteer
    )
    from_list_of_cadets = get_sorted_list_of_cadets(
        interface=interface, sort_by=SORT_BY_SURNAME
    )

    form = form_to_edit_connections(
        volunteer=volunteer,
        connected_cadets=connected_cadets,
        text=header_text,
        from_list_of_cadets=from_list_of_cadets,
    )

    return form


header_text = ListOfLines(
    [
        Line(
            "Edit volunteer and cadet connections (used to avoid putting group_allocations/parents together and to find volunteers):"
        ),
        Line(
            "Note: This will not automatically connect volunteers and group_allocations in events, nor will deleting a connection remove the connection in an event"
        ),
    ]
)


def form_to_edit_connections(
    volunteer: Volunteer,
    connected_cadets: ListOfCadets,
    text: ListOfLines,
    from_list_of_cadets: ListOfCadets,
) -> Form:
    existing_entries = rows_for_existing_entries(connected_cadets=connected_cadets)
    new_entries = row_for_new_entries(
        volunteer=volunteer,
        connected_cadets=connected_cadets,
        from_list_of_cadets=from_list_of_cadets,
    )
    footer_buttons = ButtonBar([back_menu_button])

    return Form(
        [
            ListOfLines(
                [
                    text,
                    _______________,
                    existing_entries,
                    new_entries,
                    _______________,
                    footer_buttons,
                ]
            )
        ]
    )


def rows_for_existing_entries(connected_cadets: List[Cadet]) -> ListOfLines:
    return ListOfLines(
        [get_row_for_connected_cadet(cadet) for cadet in connected_cadets]
    )


def get_row_for_connected_cadet(cadet: Cadet) -> Line:
    return Line([str(cadet), Button(button_str_for_deletion(cadet))])


def button_str_for_deletion(cadet: Cadet):
    return "Delete %s" % str(cadet)


def cadet_from_button_str(interface: abstractInterface, button_str: str) -> Cadet:
    cadet_selected = " ".join(button_str.split(" ")[1:])
    return DEPRECATE_get_cadet_given_cadet_as_str(
        interface=interface, cadet_selected=cadet_selected
    )


def row_for_new_entries(
    volunteer: Volunteer,
    connected_cadets: ListOfCadets,
    from_list_of_cadets: ListOfCadets,
) -> Line:
    list_of_cadets_to_pick_from = from_list_of_cadets.excluding_cadets_from_other_list(
        list_of_cadets=connected_cadets
    )
    list_of_cadets_similar_to_name_first = get_list_of_cadets_similar_to_name_first(
        object_with_name=volunteer, from_list_of_cadets=list_of_cadets_to_pick_from
    )

    dict_of_options = dict(
        [
            (from_cadet_to_string_in_dropdown(cadet), cadet.id)
            for cadet in list_of_cadets_similar_to_name_first
        ]
    )
    filler_row = {CADET_FILLER: CADET_FILLER}
    dict_of_options = {**filler_row, **dict_of_options}

    drop_down = dropDownInput(
        input_label="Add new connection",
        default_label=CADET_FILLER,
        dict_of_options=dict_of_options,
        input_name=CONNECTION,
    )
    return Line([drop_down, Button(ADD_CONNECTION_BUTTON_LABEL)])


def from_cadet_to_string_in_dropdown(cadet: Cadet) -> str:
    return str(cadet)


CADET_FILLER = "Choose cadet from dropdown and hit add to add connection"


def post_form_edit_cadet_volunteer_connections(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    button = interface.last_button_pressed()
    ### Buttons are back; delete button for individual cadet connection; add to add a new connection
    if back_menu_button.pressed(button):
        return previous_form(interface)
    elif button == ADD_CONNECTION_BUTTON_LABEL:
        add_connection_from_form(interface)
        interface.flush_cache_to_store()
        ## might want to do more
        return display_form_edit_cadet_volunteer_connections(interface)

    return post_form_edit_cadet_volunteer_connections_when_delete_button_pressed(
        interface
    )


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_edit_cadet_volunteer_connections
    )


def post_form_edit_cadet_volunteer_connections_when_delete_button_pressed(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    button = interface.last_button_pressed()

    volunteer = get_volunteer_from_state(interface)
    connected_cadets = DEPRECATE_get_connected_cadets(
        interface=interface, volunteer=volunteer
    )

    list_of_delete_cadet_buttons = get_list_of_delete_cadet_buttons(connected_cadets)
    if button in list_of_delete_cadet_buttons:
        delete_connection_given_form(interface=interface)
        interface.flush_cache_to_store()
        ## might want to do more
        return display_form_edit_cadet_volunteer_connections(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)


def get_list_of_delete_cadet_buttons(connected_cadets: list):
    return [button_str_for_deletion(cadet) for cadet in connected_cadets]


def add_connection_from_form(interface: abstractInterface):
    volunteer = get_volunteer_from_state(interface)
    selected_cadet_id = interface.value_from_form(CONNECTION)
    if selected_cadet_id == CADET_FILLER:
        interface.log_error(
            "You have to select a cadet from the dropdown before adding"
        )
        return
    selected_cadet = DEPRECATE_cadet_from_id_USE_get_cadet_from_id(
        interface=interface, cadet_id=selected_cadet_id
    )
    add_volunteer_connection_to_cadet_in_master_list_of_volunteers(
        interface=interface, cadet=selected_cadet, volunteer=volunteer
    )


def delete_connection_given_form(interface: abstractInterface):
    cadet = get_cadet_connection_to_delete_from_form(interface)
    volunteer = get_volunteer_from_state(interface)
    delete_connection_in_data(interface=interface, cadet=cadet, volunteer=volunteer)


def get_cadet_connection_to_delete_from_form(interface: abstractInterface) -> Cadet:
    button = interface.last_button_pressed()
    cadet = cadet_from_button_str(interface=interface, button_str=button)

    return cadet

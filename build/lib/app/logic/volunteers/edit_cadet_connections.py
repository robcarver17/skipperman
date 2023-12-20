
from typing import Union

from app.data_access.data import data
from app.logic.cadets.backend import get_list_of_cadets_as_str, get_cadet_from_list_of_cadets
from app.logic.forms_and_interfaces.abstract_form import Form, NewForm, Button, Line, ListOfLines, _______________, \
    dropDownInput
from app.logic.abstract_logic_api import initial_state_form
from app.logic.forms_and_interfaces.abstract_interface import (
    abstractInterface,
)
from app.logic.volunteers.constants import *
from app.logic.volunteers.backend import get_volunteer_from_state, get_connected_cadets
from app.objects.volunteers import Volunteer
from app.objects.cadets import Cadet

def display_form_edit_cadet_volunteer_connections(
    interface: abstractInterface,
) -> Union[Form, NewForm]:

    try:
        volunteer = get_volunteer_from_state(interface)
    except:
        interface.log_error(
            "Cadet selected no longer in list- someone else has deleted or file corruption?"
        )
        return initial_state_form

    form = form_to_edit_connections(volunteer)

    return form

def form_to_edit_connections(volunteer: Volunteer,
        ) -> Form:

    existing_entries = rows_for_existing_entries(volunteer)
    new_entries = row_for_new_entries(volunteer)
    footer_buttons = Line([Button(BACK_BUTTON_LABEL)])

    return Form([
        ListOfLines([
            "Edit volunteer and cadet connections (used to avoid putting cadets/parents together):",
            _______________,
            existing_entries,
            new_entries,
            _______________,
            footer_buttons
        ])
    ])

def rows_for_existing_entries(volunteer: Volunteer) -> ListOfLines:
    connected_cadets = get_connected_cadets(volunteer)
    return ListOfLines([
        get_row_for_connected_cadet(cadet) for cadet in connected_cadets
    ])


def get_row_for_connected_cadet(cadet: Cadet) -> Line:
    return Line(
        [str(cadet), Button(button_str_for_deletion(cadet))]
    )

def button_str_for_deletion(cadet: Cadet):
    return "Delete %s" % str(cadet)

def cadet_from_button_str(button_str: str) -> Cadet:
    cadet_selected = " ".join(button_str.split(" ")[1:])
    return get_cadet_from_list_of_cadets(cadet_selected)

def row_for_new_entries(volunteer: Volunteer) -> Line:
    list_of_cadets_as_str =get_list_of_cadets_as_str()
    list_of_cadets_as_str.sort()
    list_of_cadets_as_str.insert(0, CADET_FILLER)
    dict_of_options = dict([(cadet_str, cadet_str) for cadet_str in list_of_cadets_as_str])
    drop_down = dropDownInput(input_label="Add new connection",
                              default_label=CADET_FILLER,
                              dict_of_options=dict_of_options,
                              input_name=CONNECTION,
                              )
    return Line([drop_down, Button(ADD_CONNECTION_BUTTON_LABEL)])

CADET_FILLER = "Choose cadet from dropdown and hit add to add connection"

def post_form_edit_cadet_volunteer_connections(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    button = interface.last_button_pressed()
    ### Buttons are back; delete button for individual cadet connection; add to add a new connection
    if button==BACK_BUTTON_LABEL:
        return NewForm(VIEW_INDIVIDUAL_VOLUNTEER_STAGE)
    elif button==ADD_CONNECTION_BUTTON_LABEL:
        add_connection_from_form(interface)
        ## might want to do more
        return display_form_edit_cadet_volunteer_connections(interface)

    list_of_delete_cadet_buttons = get_list_of_delete_cadet_buttons(interface)
    if button in list_of_delete_cadet_buttons:
        delete_connection_given_form(interface=interface)
        ## might want to do more
        return display_form_edit_cadet_volunteer_connections(interface)
    else:
        raise Exception("Weirdly named button pressed")

def get_list_of_delete_cadet_buttons(interface: abstractInterface):
    volunteer = get_volunteer_from_state(interface)
    connected_cadets = get_connected_cadets(volunteer)

    return [button_str_for_deletion(cadet) for cadet in connected_cadets]

def add_connection_from_form(interface: abstractInterface):
    volunteer = get_volunteer_from_state(interface)
    selected_cadet_as_str = interface.value_from_form(CONNECTION)
    if selected_cadet_as_str == CADET_FILLER:
        interface.log_error("You have to select a cadet from the dropdown before adding")
        return
    selected_cadet = get_cadet_from_list_of_cadets(selected_cadet_as_str)
    add_connection_to_data(cadet=selected_cadet, volunteer=volunteer)

def add_connection_to_data(cadet: Cadet, volunteer: Volunteer):
    existing_connections = data.data_list_of_cadet_volunteer_associations.read()
    existing_connections.add(cadet_id=cadet.id, volunteer_id=volunteer.id)
    data.data_list_of_cadet_volunteer_associations.write(existing_connections)


def delete_connection_given_form(interface: abstractInterface):
    button = interface.last_button_pressed()
    cadet = cadet_from_button_str(button)
    volunteer = get_volunteer_from_state(interface)
    delete_connection_in_data(cadet=cadet, volunteer=volunteer)

def delete_connection_in_data(cadet: Cadet, volunteer: Volunteer):
    existing_connections = data.data_list_of_cadet_volunteer_associations.read()
    existing_connections.delete(cadet_id=cadet.id, volunteer_id=volunteer.id)
    data.data_list_of_cadet_volunteer_associations.write(existing_connections)

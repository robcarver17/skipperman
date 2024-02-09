from typing import Union

from app.backend.group_allocations.cadet_event_allocations import get_list_of_cadets_in_master_event
from app.backend.volunteers.volunteer_allocation import get_volunteer_at_event, get_volunteer_from_id
from app.backend.data.volunteer_allocation import remove_volunteer_and_cadet_association_at_event, \
    add_volunteer_and_cadet_association_for_existing_volunteer

from app.backend.cadets import cadet_from_id, get_cadet_from_list_of_cadets


from app.logic.abstract_interface import abstractInterface

from app.logic.events.constants import EDIT_VOLUNTEER_ROTA_EVENT_STAGE
from app.logic.events.events_in_state import get_event_from_state

from app.logic.volunteers.constants import BACK_BUTTON_LABEL, ADD_CONNECTION_BUTTON_LABEL, CONNECTION
from app.logic.volunteers.edit_cadet_connections import form_to_edit_connections, get_list_of_delete_cadet_buttons, \
    get_cadet_connection_to_delete_from_form, CADET_FILLER
from app.logic.volunteers.volunteer_state import get_volunteer_id_selected_from_state

from app.objects.cadets import ListOfCadets

from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_lines import ListOfLines


def display_form_edit_cadet_connections_from_rota(interface: abstractInterface):
    volunteer_id = get_volunteer_id_selected_from_state(interface) ## NEEDS TO BE SET
    event =get_event_from_state(interface)
    volunteer = get_volunteer_from_id(volunteer_id)
    connected_cadets = list_of_connected_cadets(interface)

    header_text = ListOfLines([
        "Following are connected cadets for volunteer %s at event %s - add or modify if required" % (
        volunteer.name, str(event))])

    list_of_cadets_at_event = get_list_of_cadets_in_master_event(event)

    form = form_to_edit_connections(volunteer=volunteer, connected_cadets=connected_cadets,
                                    from_list_of_cadets=list_of_cadets_at_event,
                                    text=header_text)

    return form

def list_of_connected_cadets(interface: abstractInterface):
    volunteer_id = get_volunteer_id_selected_from_state(interface) ## NEEDS TO BE SET
    event =get_event_from_state(interface)
    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    cadet_ids = volunteer_at_event.list_of_associated_cadet_id


    connected_cadets = ListOfCadets([cadet_from_id(cadet_id) for cadet_id in cadet_ids])

    return connected_cadets

def post_form_edit_cadet_connections_from_rota(
    interface: abstractInterface,
) -> Union[Form, NewForm]:

    button = interface.last_button_pressed()
    ### Buttons are back; delete button for individual cadet connection; add to add a new connection
    if button==BACK_BUTTON_LABEL:
        return NewForm(EDIT_VOLUNTEER_ROTA_EVENT_STAGE)
    elif button==ADD_CONNECTION_BUTTON_LABEL:
        add_event_connection_from_form(interface)
        ## might want to do more
        return display_form_edit_cadet_connections_from_rota(interface)

    connected_cadets = list_of_connected_cadets(interface)

    list_of_delete_cadet_buttons = get_list_of_delete_cadet_buttons(connected_cadets)
    if button in list_of_delete_cadet_buttons:
        delete_event_connection_given_form(interface=interface)
        ## might want to do more
        return display_form_edit_cadet_connections_from_rota(interface)
    else:
        raise Exception("Weirdly named button %s pressed" % button)


def delete_event_connection_given_form(interface: abstractInterface):
    cadet = get_cadet_connection_to_delete_from_form(interface)
    volunteer_id = get_volunteer_id_selected_from_state(interface)
    event = get_event_from_state(interface)
    print("Remove %s %s %s" % (cadet.id, volunteer_id, str(event)))
    remove_volunteer_and_cadet_association_at_event(cadet_id=cadet.id,
                                                    volunteer_id=volunteer_id,
                                                    event=event)


def add_event_connection_from_form(interface: abstractInterface):

    selected_cadet_as_str = interface.value_from_form(CONNECTION)
    if selected_cadet_as_str == CADET_FILLER:
        interface.log_error("You have to select a cadet from the dropdown before adding")
        return
    volunteer_id = get_volunteer_id_selected_from_state(interface)
    selected_cadet = get_cadet_from_list_of_cadets(selected_cadet_as_str)
    event = get_event_from_state(interface)
    add_volunteer_and_cadet_association_for_existing_volunteer(volunteer_id=volunteer_id,
                                                               cadet_id=selected_cadet.id,
                                                               event_id=event.id)

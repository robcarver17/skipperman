from app.backend.events.list_of_events import (
    get_event_from_id,
    get_event_from_list_of_events_given_event_description,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import Event
from app.objects.utilities.exceptions import missing_data


def get_event_from_state(interface: abstractInterface, default = missing_data) -> Event:
    id = get_event_id_from_state(interface, default=missing_data)
    if id is missing_data:
        return default

    return get_event_from_id(object_store=interface.object_store, event_id=id)

def clear_event_id_stored_in_state(interface: abstractInterface):
    interface.clear_persistent_value(EVENT)

def get_event_id_from_state(interface: abstractInterface, default = missing_data) -> str:
    return interface.get_persistent_value(EVENT, default=default)


def update_state_for_specific_event(interface: abstractInterface, event: Event):
    id = event.id
    interface.set_persistent_value(EVENT, id)


EVENT = "event"

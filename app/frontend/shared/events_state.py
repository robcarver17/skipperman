from app.backend.events.list_of_events import (
    get_event_from_id,
    get_event_from_list_of_events_given_event_description,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import Event


def get_event_from_state(interface: abstractInterface) -> Event:
    id = get_event_id_from_state(interface)
    return get_event_from_id(object_store=interface.object_store, event_id=id)


def get_event_id_from_state(interface: abstractInterface) -> str:
    return interface.get_persistent_value(EVENT)


def update_state_for_specific_event_given_event_description(
    interface: abstractInterface, event_description: str
):
    event = get_event_from_list_of_events_given_event_description(
        object_store=interface.object_store, event_description=event_description
    )
    id = event.id
    interface.set_persistent_value(EVENT, id)


EVENT = "event"
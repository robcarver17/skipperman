from app.backend.events import DEPRECATE_get_list_of_all_events
from app.logic.events.constants import EVENT
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import Event


def get_event_from_state(interface: abstractInterface) -> Event:
    id = get_event_id_from_state(interface)
    return get_event_given_id(interface=interface, id=id)


def get_event_given_id(interface: abstractInterface, id: str) -> Event:
    list_of_events = DEPRECATE_get_list_of_all_events(interface)
    return list_of_events.object_with_id(id)


def get_event_id_from_state(interface: abstractInterface) -> str:
    return interface.get_persistent_value(EVENT)


def get_event_from_list_of_events_given_event_description(
    interface: abstractInterface, event_description: str
) -> Event:
    list_of_events = DEPRECATE_get_list_of_all_events(interface)

    return list_of_events.event_with_description(event_description)


def update_state_for_specific_event_given_event_description(
    interface: abstractInterface, event_description: str
):
    event = get_event_from_list_of_events_given_event_description(
        interface=interface, event_description=event_description
    )
    print("event descr %s %s" % (event_description, str(event)))
    id = event.id
    print("id %s" % id)
    interface.set_persistent_value(EVENT, id)

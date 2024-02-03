from app.backend.events import get_list_of_events
from app.logic.events.constants import EVENT
from app.logic.abstract_interface import abstractInterface
from app.objects.events import Event


def get_event_from_state(interface: abstractInterface) -> Event:
    id = get_event_id_from_state(interface)
    print("id %s" % id)
    return get_event_given_id(id)

def get_event_given_id(id: str) -> Event:
    list_of_events = get_list_of_events()
    print("list of events %s" % str(list_of_events))
    return list_of_events.has_id(id)


def get_event_id_from_state(interface: abstractInterface) -> str:
    return interface.get_persistent_value(EVENT)


def get_event_from_list_of_events_given_event_description(event_description: str) -> Event:
    list_of_events = get_list_of_events()

    return list_of_events.event_with_description(event_description)



def update_state_for_specific_event_given_event_description(interface: abstractInterface, event_description: str):
    event = get_event_from_list_of_events_given_event_description(event_description)
    print("event descr %s %s" % (event_description, str(event)))
    id = event.id
    print("id %s" % id)
    interface.set_persistent_value(EVENT, id)
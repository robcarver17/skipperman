from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import (
    ListOfEvents,
    SORT_BY_START_DSC,
    SORT_BY_START_ASC,
    SORT_BY_NAME,
    Event, ALL_EVENTS,
)

from app.data_access.store.object_store import ObjectStore
from app.objects.utilities.exceptions import arg_not_passed


def list_of_previously_used_event_names(object_store: ObjectStore) -> list:
    list_of_events = get_list_of_events(object_store)
    event_names = [event.event_name for event in list_of_events]
    return list(set(event_names))


def add_new_verified_event(interface: abstractInterface, event: Event):
    interface.update(
        interface.object_store.data_api.data_list_of_events.add_event, event=event
    )


def get_event_from_id(
    object_store: ObjectStore, event_id: str, default=arg_not_passed
) -> Event:
    return object_store.get(
        object_store.data_api.data_list_of_events.get_event_from_id,
        event_id=event_id,
        default=default,
    )


def get_event_from_list_of_events_given_event_description(
    object_store: ObjectStore, event_description: str
) -> Event:
    list_of_events = get_list_of_events(object_store)

    return list_of_events.event_with_description(event_description)


def get_sorted_list_of_events(
    object_store: ObjectStore, sort_by=SORT_BY_START_DSC
) -> ListOfEvents:
    return object_store.get(
        object_store.data_api.data_list_of_events.read, sort_by=sort_by
    )


def get_list_of_events(object_store: ObjectStore) -> ListOfEvents:
    return object_store.get(object_store.data_api.data_list_of_events.read)


all_sort_types_for_event_list = [SORT_BY_START_ASC, SORT_BY_START_DSC, SORT_BY_NAME]



def get_list_of_last_N_events(
    object_store: ObjectStore,
    excluding_event: Event = arg_not_passed,
    only_events_before_excluded_event: bool = True,
    N_events: int = ALL_EVENTS,
) -> ListOfEvents:
    return object_store.get(
        object_store.data_api.data_list_of_events.get_list_of_last_N_events,
        excluding_event=excluding_event,
        only_events_before_excluded_event=only_events_before_excluded_event,
        N_events=N_events
    )



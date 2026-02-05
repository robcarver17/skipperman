from copy import copy

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import (
    ListOfEvents,
    SORT_BY_START_DSC,
    SORT_BY_START_ASC,
    SORT_BY_NAME,
    Event,
)

from app.data_access.store.object_store import ObjectStore
from app.objects.utilities.exceptions import arg_not_passed


def list_of_previously_used_event_names(object_store: ObjectStore) -> list:
    list_of_events = get_list_of_events(object_store)
    event_names = [event.event_name for event in list_of_events]
    return list(set(event_names))


def add_new_verified_event(interface: abstractInterface, event: Event):
    interface.update(
        interface.object_store.data_api.data_list_of_events.add_event,
        event=event
    )

def get_event_from_id(
    object_store: ObjectStore, event_id: str, default=arg_not_passed
) -> Event:
    return object_store.get(object_store.data_api.data_list_of_events.get_event_from_id,
                            event_id=event_id, default=default)


def get_event_from_list_of_events_given_event_description(
    object_store: ObjectStore, event_description: str
) -> Event:
    list_of_events = get_list_of_events(object_store)

    return list_of_events.event_with_description(event_description)


def get_sorted_list_of_events(
    object_store: ObjectStore, sort_by=SORT_BY_START_DSC
) -> ListOfEvents:
    return object_store.get(object_store.data_api.data_list_of_events.read,
                            sort_by=sort_by)

def get_list_of_events(object_store: ObjectStore) -> ListOfEvents:
    return object_store.get(object_store.data_api.data_list_of_events.read)


all_sort_types_for_event_list = [SORT_BY_START_ASC, SORT_BY_START_DSC, SORT_BY_NAME]

ALL_EVENTS = 99999999999999


def get_list_of_last_N_events(
    object_store: ObjectStore,
    excluding_event: Event = arg_not_passed,
    only_events_before_excluded_event: bool = True,
    N_events: int = ALL_EVENTS,
) -> ListOfEvents:
    list_of_events_sorted_by_date_asc = copy(get_sorted_list_of_events(object_store, sort_by=SORT_BY_START_ASC))
    list_of_events = remove_event_and_possibly_past_events_and_sort(
        list_of_events_sorted_by_date_asc=list_of_events_sorted_by_date_asc,
        excluding_event=excluding_event,
        only_events_before_excluded_event=only_events_before_excluded_event,
    )

    list_of_events = get_N_most_recent_events_newest_last(
        list_of_events, N_events=N_events
    )

    return list_of_events


def remove_event_and_possibly_past_events_and_sort(
    list_of_events_sorted_by_date_asc: ListOfEvents,
    excluding_event: Event = arg_not_passed,
    only_events_before_excluded_event: bool = True,
):

    try:  # weird not a singleton error
        if excluding_event == arg_not_passed:
            return list_of_events_sorted_by_date_asc
    except:
        pass

    idx_of_event = list_of_events_sorted_by_date_asc.index_of_id(excluding_event.id)
    if only_events_before_excluded_event:
        list_of_events_sorted_by_date_asc = list_of_events_sorted_by_date_asc[
            :idx_of_event
        ]  ## only those that occured before this event
    else:
        list_of_events_sorted_by_date_asc.pop(idx_of_event)

    return ListOfEvents(list_of_events_sorted_by_date_asc)


def get_N_most_recent_events_newest_last(
    list_of_events: ListOfEvents,
    N_events: int = ALL_EVENTS,
) -> ListOfEvents:
    list_of_events_sorted_by_date_desc = (
        list_of_events.sort_by_start_date_asc()
    )  ## newest last

    return ListOfEvents(list_of_events_sorted_by_date_desc[-N_events:])

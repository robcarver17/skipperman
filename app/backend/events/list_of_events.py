from copy import copy

from app.data_access.store.object_definitions import (
    object_definition_for_list_of_events,
)
from app.objects.abstract_objects.abstract_buttons import ButtonBar, Button
from app.objects.events import (
    ListOfEvents,
    SORT_BY_START_DSC,
    SORT_BY_START_ASC,
    SORT_BY_NAME,
    Event,
)

from app.data_access.store.object_store import ObjectStore
from app.objects.exceptions import arg_not_passed
from build.lib.app.objects.exceptions import arg_not_passed


def list_of_previously_used_event_names(object_store: ObjectStore) -> list:
    list_of_events = get_list_of_events(object_store)
    event_names = [event.event_name for event in list_of_events]
    return list(set(event_names))


def add_new_verified_event(object_store: ObjectStore, event: Event):
    list_of_events = get_list_of_events(object_store)
    list_of_events.add(event)
    update_list_of_events(
        object_store=object_store, updated_list_of_events=list_of_events
    )


def get_event_from_id(
    object_store: ObjectStore, event_id: str, default=arg_not_passed
) -> Event:
    list_of_events = get_list_of_events(object_store)
    return list_of_events.event_with_id(event_id, default=default)


def get_event_from_list_of_events_given_event_description(
    object_store: ObjectStore, event_description: str
) -> Event:
    list_of_events = get_list_of_events(object_store)

    return list_of_events.event_with_description(event_description)


def get_sorted_list_of_events(
    object_store: ObjectStore, sort_by=SORT_BY_START_DSC
) -> ListOfEvents:
    list_of_events = get_list_of_events(object_store)
    list_of_events = list_of_events.sort_by(sort_by)

    return list_of_events


def get_list_of_events(object_store: ObjectStore) -> ListOfEvents:
    return object_store.get(object_definition_for_list_of_events)


def update_list_of_events(
    object_store: ObjectStore, updated_list_of_events: ListOfEvents
):
    object_store.update(
        new_object=updated_list_of_events,
        object_definition=object_definition_for_list_of_events,
    )


all_sort_types_for_event_list = [SORT_BY_START_ASC, SORT_BY_START_DSC, SORT_BY_NAME]
sort_buttons_for_event_list = ButtonBar(
    [Button(sortby, nav_button=True) for sortby in all_sort_types_for_event_list]
)

ALL_EVENTS = 99999999999999


def get_list_of_last_N_events(
    object_store: ObjectStore,
    excluding_event: Event,
    only_events_before_excluded_event: bool = True,
    N_events: int = ALL_EVENTS,
) -> ListOfEvents:
    list_of_events = copy(get_list_of_events(object_store))
    list_of_events = remove_event_and_possibly_past_events(
        list_of_events,
        excluding_event=excluding_event,
        only_events_before_excluded_event=only_events_before_excluded_event,
    )

    list_of_events = get_N_most_recent_events_newest_last(
        list_of_events, N_events=N_events
    )

    return list_of_events


def remove_event_and_possibly_past_events(
    list_of_events: ListOfEvents,
    excluding_event: Event,
    only_events_before_excluded_event: bool = True,
):
    list_of_events_sorted_by_date_desc = (
        list_of_events.sort_by_start_date_asc()
    )  ## newest last

    if excluding_event is not arg_not_passed:
        idx_of_event = list_of_events_sorted_by_date_desc.index_of_id(
            excluding_event.id
        )
        if only_events_before_excluded_event:
            list_of_events_sorted_by_date_desc = list_of_events_sorted_by_date_desc[
                :idx_of_event
            ]  ## only those that occured before this event
        else:
            list_of_events_sorted_by_date_desc.pop(idx_of_event)

    return ListOfEvents(list_of_events_sorted_by_date_desc)


def get_N_most_recent_events_newest_last(
    list_of_events: ListOfEvents,
    N_events: int = ALL_EVENTS,
) -> ListOfEvents:

    list_of_events_sorted_by_date_desc = (
        list_of_events.sort_by_start_date_asc()
    )  ## newest last

    return ListOfEvents(list_of_events_sorted_by_date_desc[-N_events:])

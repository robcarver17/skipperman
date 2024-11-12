from app.data_access.store.data_access import DataLayer

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.events import EventData

from app.objects.events import (
    Event,
    ListOfEvents,
    SORT_BY_START_DSC,
)


def DEPRECATE_get_sorted_list_of_events(
    interface: abstractInterface, sort_by=SORT_BY_START_DSC
) -> ListOfEvents:
    list_of_events = DEPRECATE_get_list_of_all_events(interface)
    list_of_events = list_of_events.sort_by(sort_by)

    return list_of_events


def get_sorted_list_of_events(
    data_layer: DataLayer, sort_by=SORT_BY_START_DSC
) -> ListOfEvents:
    list_of_events = get_list_of_all_events(data_layer)
    list_of_events = list_of_events.sort_by(sort_by)

    return list_of_events


def get_list_of_all_events(data_layer: DataLayer) -> ListOfEvents:
    event_data = EventData(data_layer)
    return event_data.list_of_events


def get_event_from_id(data_layer: DataLayer, event_id: str) -> Event:
    event_data = EventData(data_layer)
    return event_data.get_event_from_id(event_id)


def DEPRECATE_get_list_of_all_events(interface: abstractInterface) -> ListOfEvents:
    event_data = EventData(interface.data)
    return event_data.list_of_events


def get_event_from_list_of_events_given_event_description(
    interface: abstractInterface, event_description: str
) -> Event:
    list_of_events = DEPRECATE_get_list_of_all_events(interface)

    return list_of_events.event_with_description(event_description)

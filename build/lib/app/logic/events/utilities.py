from app.data_access.data import data
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.logic.events.constants import (
    EVENT,
    SORT_BY_START_ASC,
    SORT_BY_START_DSC,
    SORT_BY_NAME,
)
from app.objects.events import Event, ListOfEvents


def get_event_from_state(interface: abstractInterface) -> Event:
    return get_event_from_list_of_events(get_specific_event_str_from_state(interface))


def get_specific_event_str_from_state(interface: abstractInterface) -> str:
    return interface.get_persistent_value(EVENT)


def get_event_from_list_of_events(event_selected: str) -> Event:
    list_of_events = get_list_of_events()
    list_of_events_as_str = [str(event) for event in list_of_events]

    event_idx = list_of_events_as_str.index(event_selected)
    return list_of_events[event_idx]


def get_list_of_events(sort_by=SORT_BY_START_DSC) -> ListOfEvents:
    list_of_events = data.data_list_of_events.read()
    if sort_by == SORT_BY_START_DSC:
        return list_of_events.sort_by_start_date_desc()
    elif sort_by == SORT_BY_START_ASC:
        return list_of_events.sort_by_start_date_asc()
    elif sort_by == SORT_BY_NAME:
        return list_of_events.sort_by_name()
    else:
        return list_of_events


def get_event_from_id(id: str) -> Event:
    list_of_events = data.data_list_of_events.read()
    return list_of_events.has_id(id)


def confirm_event_exists(event_selected):
    list_of_events = get_list_of_events()
    list_of_events_as_str = [str(event) for event in list_of_events]
    assert event_selected in list_of_events_as_str


def update_state_for_specific_event(interface: abstractInterface, event_selected: str):
    interface.set_persistent_value(EVENT, event_selected)

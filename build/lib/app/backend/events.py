import datetime
import re
from dataclasses import dataclass

from app.data_access.store.data_access import DataLayer

from app.objects.abstract_objects.abstract_buttons import ButtonBar, Button
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.events import EventData
from app.data_access.configuration.configuration import (
    SIMILARITY_LEVEL_TO_WARN_NAME,
    SIMILARITY_LEVEL_TO_WARN_DATE,
)

from app.objects.events import (
    Event,
    ListOfEvents,
    SORT_BY_START_DSC,
    SORT_BY_START_ASC,
    SORT_BY_NAME,
    default_event,
)


def verify_event_and_warn(interface: abstractInterface, event: Event) -> str:
    warn_text = ""
    if contains_2_more_digits(event.event_name):
        warn_text += "Looks like event name contains a year - don't do that! "
    if len(event.event_name) < 5:
        warn_text += "Event name seems a bit short. "
    if event.start_date < datetime.date.today():
        warn_text += "Event started in the past. "
    if event.end_date < event.start_date:
        warn_text += "Event ends before it starts. "
    if event.duration == 1:
        warn_text += "Event is only one day long. "

    if event.duration > 8:
        warn_text += "Event is more than a week long. "

    if event.contains_groups and not event.contains_cadets:
        warn_text += "Event with training groups must also have cadets. "

    if event.contains_volunteers and not event.contains_cadets:
        warn_text += "Event with volunteers must also have cadets (may change in future version). "

    warn_text += warning_for_similar_events(interface=interface, event=event)

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text


def contains_2_more_digits(string: str) -> bool:
    return len(re.findall(r"\d", string)) > 1


def warning_for_similar_events(interface: abstractInterface, event: Event) -> str:
    existing_events = DEPRECATE_get_sorted_list_of_events(interface)
    similar_events = existing_events.similar_events(
        event,
        name_threshold=SIMILARITY_LEVEL_TO_WARN_NAME,
        date_threshold=SIMILARITY_LEVEL_TO_WARN_DATE,
    )

    if len(similar_events) > 0:
        similar_events_str = ", ".join(
            [str(other_event) for other_event in similar_events]
        )
        return "Following events look awfully similar:\n %s" % similar_events_str
    else:
        return ""


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


def list_of_previously_used_event_names(interface: abstractInterface) -> list:
    list_of_events = DEPRECATE_get_list_of_all_events(interface)
    event_names = [event.event_name for event in list_of_events]
    return list(set(event_names))


def confirm_event_exists_given_description(
    interface: abstractInterface, event_description: str
):
    list_of_events = DEPRECATE_get_list_of_all_events(interface)

    ## fails if missing
    __ = list_of_events.event_with_description(event_description)


all_sort_types_for_event_list = [SORT_BY_START_ASC, SORT_BY_START_DSC, SORT_BY_NAME]
sort_buttons_for_event_list = ButtonBar(
    [Button(sortby, nav_button=True) for sortby in all_sort_types_for_event_list]
)


@dataclass
class EventAndVerificationText:
    event: Event = default_event
    verification_text: str = ("",)

    @property
    def is_default(self) -> bool:
        return self.event == default_event


event_and_text_if_first_time = EventAndVerificationText(
    event=default_event, verification_text=""
)


def add_new_verified_event(interface: abstractInterface, event: Event):
    event_data = EventData(interface.data)
    event_data.add_event(event)

def get_event_from_id(data_layer: DataLayer, event_id:str) -> Event:
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

import datetime

from app.objects.abstract_objects.abstract_buttons import ButtonBar, Button
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.events import DEPRECATED_get_list_of_all_events, get_list_of_all_events
from app.data_access.configuration.configuration import SIMILARITY_LEVEL_TO_WARN_NAME, SIMILARITY_LEVEL_TO_WARN_DATE
from app.data_access.data import DEPRECATED_data

from app.objects.events import Event, ListOfEvents, SORT_BY_START_DSC, SORT_BY_START_ASC, SORT_BY_NAME


def verify_event_and_warn(event: Event) -> str:
    warn_text = ""
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
        warn_text +="Event with training groups must also have cadets. "

    if event.contains_volunteers and not event.contains_cadets:
        warn_text +="Event with volunteers must also have cadets (may change in future version). "

    warn_text += warning_for_similar_events(event=event)

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text


    return warn_text


def warning_for_similar_events(event: Event) -> str:
    existing_events = DEPRECATE_get_sorted_list_of_events()
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




def DEPRECATE_get_sorted_list_of_events(sort_by=SORT_BY_START_DSC) -> ListOfEvents:
    list_of_events = DEPRECATED_get_list_of_all_events()
    list_of_events = list_of_events.sort_by(sort_by)

    return list_of_events

def get_sorted_list_of_events(interface: abstractInterface, sort_by=SORT_BY_START_DSC) -> ListOfEvents:
    list_of_events = get_list_of_all_events(interface)
    list_of_events = list_of_events.sort_by(sort_by)

    return list_of_events


def list_of_previously_used_event_names() -> list:
    list_of_events = DEPRECATED_get_list_of_all_events()
    event_names = [event.event_name for event in list_of_events]
    return list(set(event_names))



def DEPRECATE_get_event_from_id(id: str) -> Event:
    list_of_events = DEPRECATED_get_list_of_all_events()
    return list_of_events.has_id(id)


def confirm_event_exists_given_description(event_description):
    list_of_events = DEPRECATED_get_list_of_all_events()

    ## fails if missing
    __ = list_of_events.event_with_description(event_description)


def is_wa_field_mapping_setup_for_event(event: Event) -> bool:
    try:
        wa_mapping_dict = DEPRECATED_data.data_wa_field_mapping.read(event.id)

        if len(wa_mapping_dict) == 0:
            return False
        else:
            return True
    except:
        return False


all_sort_types_for_event_list = [SORT_BY_START_ASC, SORT_BY_START_DSC, SORT_BY_NAME]
sort_buttons_for_event_list = ButtonBar([Button(sortby, nav_button=True) for sortby in all_sort_types_for_event_list])

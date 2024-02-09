import datetime

from app.backend.data.events import get_list_of_all_events
from app.data_access.configuration.configuration import SIMILARITY_LEVEL_TO_WARN_NAME, SIMILARITY_LEVEL_TO_WARN_DATE

from app.objects.events import Event, ListOfEvents,  SORT_BY_START_DSC


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

    warn_text += warning_for_similar_events(event=event)

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text


def warning_for_similar_events(event: Event) -> str:
    existing_events = get_sorted_list_of_events()
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




def get_sorted_list_of_events(sort_by=SORT_BY_START_DSC) -> ListOfEvents:
    list_of_events = get_list_of_all_events()
    list_of_events = list_of_events.sort_by(sort_by)

    return list_of_events




def get_event_from_id(id: str) -> Event:
    list_of_events = get_list_of_all_events()
    return list_of_events.has_id(id)


def confirm_event_exists_given_description(event_description):
    list_of_events = get_list_of_all_events()

    ## fails if missing
    __ = list_of_events.event_with_description(event_description)



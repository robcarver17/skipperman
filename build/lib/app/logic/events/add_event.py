import datetime
from app.data_access.api.generic_api import GenericDataApi
from app.data_access.configuration.configuration import SIMILARITY_LEVEL_TO_WARN_NAME, SIMILARITY_LEVEL_TO_WARN_DATE
from app.objects.events import Event

def verify_event_and_warn(data: GenericDataApi, event: Event)->str:
    warn_text = ""
    if len(event.event_name)<5:
        warn_text+="Event name seems a bit short. "
    if event.start_date<datetime.date.today():
        warn_text+="Event started in the past. "
    if event.end_date<event.start_date:
        warn_text+="Event ends before it starts. "
    if event.end_date==event.start_date:
        warn_text+="Event is only one day long. "

    warn_text+=warning_for_similar_events(data=data, event=event)

    if len(warn_text)>0:
        warn_text="DOUBLE CHECK BEFORE ADDING: "+warn_text

    return warn_text


def warning_for_similar_events(data: GenericDataApi, event: Event) -> str:
    existing_events = data.data_list_of_events.read()
    similar_events = existing_events.similar_events(
        event,
        name_threshold=SIMILARITY_LEVEL_TO_WARN_NAME,
        date_threshold=SIMILARITY_LEVEL_TO_WARN_DATE
    )

    if len(similar_events) > 0:
        similar_events_str = ", ".join([str(other_event) for other_event in similar_events])
        return "Following events look awfully similar:\n %s" % similar_events_str
    else:
        return ""


def add_new_verified_event(event: Event, data: GenericDataApi):
    data.data_list_of_events.add(event)


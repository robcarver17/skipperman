import datetime
import re
from dataclasses import dataclass

from app.data_access.store.object_store import ObjectStore

from app.backend.events.list_of_events import get_sorted_list_of_events
from app.data_access.configuration.configuration import (
    SIMILARITY_LEVEL_TO_WARN_NAME,
)

from app.objects.events import Event, default_event


def verify_event_and_warn(object_store: ObjectStore, event: Event) -> str:
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

    if event.duration > 7:
        warn_text += "Event is more than a week long. Skipperman does not support events more than a week in length."

    warn_text += warning_for_similar_events(object_store=object_store, event=event)

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text


def contains_2_more_digits(string: str) -> bool:
    return len(re.findall(r"\d", string)) > 1


def warning_for_similar_events(object_store: ObjectStore, event: Event) -> str:
    existing_events = get_sorted_list_of_events(object_store)
    similar_events = existing_events.similar_events(event)

    if len(similar_events) > 0:
        similar_events_str = ", ".join(
            [str(other_event) for other_event in similar_events]
        )
        return "Following events look awfully similar:\n %s" % similar_events_str
    else:
        return ""


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

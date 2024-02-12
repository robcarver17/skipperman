from app.data_access.data import data
from app.objects.events import Event

from app.objects.cadet_at_event import ListOfCadetsAtEvent, ListOfIdentifiedCadetsAtEvent

def load_cadets_at_event(event: Event) -> ListOfCadetsAtEvent:
    return data.data_cadets_at_event.read(event_id=event.id)

def load_identified_cadets_at_event(event: Event) -> ListOfIdentifiedCadetsAtEvent:
    return data.data_identified_cadets_at_event.read(event_id=event.id)

def save_identified_cadets_at_event(event: Event, list_of_cadets_at_event: ListOfIdentifiedCadetsAtEvent):
    data.data_identified_cadets_at_event.write(list_of_cadets_at_event=list_of_cadets_at_event, event_id=event.id)
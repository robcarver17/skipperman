from typing import List

from app.data_access.data import data
from app.objects.events import Event

from app.objects.cadet_at_event import ListOfCadetsAtEvent, ListOfIdentifiedCadetsAtEvent
from app.objects.dinghies import ListOfCadetAtEventWithDinghies

def cadet_id_at_event_given_row_id(event: Event, row_id: str) -> str:
    identified_cadets_at_event = load_identified_cadets_at_event(event)
    cadet_id = identified_cadets_at_event.cadet_id_given_row_id(row_id=row_id)

    return cadet_id

def list_of_row_ids_at_event_given_cadet_id(event: Event, cadet_id: str) -> List[str]:
    identified_cadets_at_event = load_identified_cadets_at_event(event)
    list_of_row_ids = identified_cadets_at_event.list_of_row_ids_given_cadet_id(cadet_id)

    return list_of_row_ids


def load_cadets_at_event(event: Event) -> ListOfCadetsAtEvent:
    return data.data_cadets_at_event.read(event_id=event.id)

def save_cadets_at_event(event: Event , list_of_cadets_at_event: ListOfCadetsAtEvent):
    return data.data_cadets_at_event.write(list_of_cadets_at_event=list_of_cadets_at_event, event_id=event.id)

def load_identified_cadets_at_event(event: Event) -> ListOfIdentifiedCadetsAtEvent:
    return data.data_identified_cadets_at_event.read(event_id=event.id)

def save_identified_cadets_at_event(event: Event, list_of_cadets_at_event: ListOfIdentifiedCadetsAtEvent):
    data.data_identified_cadets_at_event.write(list_of_cadets_at_event=list_of_cadets_at_event, event_id=event.id)


def load_list_of_cadets_at_event_with_dinghies(event: Event) -> ListOfCadetAtEventWithDinghies:
    cadets_with_dinghies = data.data_list_of_cadets_with_dinghies_at_event.read(event.id)

    return cadets_with_dinghies

def save_list_of_cadets_at_event_with_dinghies(event: Event,
                                                    cadets_with_club_dinghies_at_event: ListOfCadetAtEventWithDinghies):

    data.data_list_of_cadets_with_dinghies_at_event.write(event_id=event.id, people_and_boats=cadets_with_club_dinghies_at_event)




from typing import List

from app.objects.cadets import Cadet, ListOfCadets

from app.objects.composed.people_at_event_with_club_dinghies import (
    DictOfPeopleAndClubDinghiesAtEvent,
)

from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore


def is_a_club_dinghy_allocated_for_list_of_cadets_on_any_day_at_event(
    object_store: ObjectStore, event: Event, list_of_cadets: ListOfCadets
) -> List[bool]:
    return [
        is_a_club_dinghy_allocated_for_cadet_on_any_day_at_event(
            object_store=object_store, cadet=cadet, event=event
        )
        for cadet in list_of_cadets
    ]


def is_a_club_dinghy_allocated_for_cadet_on_any_day_at_event(
    object_store: ObjectStore, event: Event, cadet: Cadet
) -> bool:
    return object_store.get(object_store.data_api.data_list_of_cadets_at_event_with_club_dinghies.is_a_club_dinghy_allocated_for_cadet_on_any_day_at_event,
                            event_id=event.id,
                            cadet_id=cadet.id)



def get_dict_of_volunteers_and_club_dinghies_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfPeopleAndClubDinghiesAtEvent:
    return object_store.get(object_store.data_api.data_list_of_volunteers_at_event_with_club_dinghies.read_dict_of_volunteers_and_club_dinghies_at_event,
                            event_id=event.id)

def get_dict_of_cadets_and_club_dinghies_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfPeopleAndClubDinghiesAtEvent:
    return object_store.get(object_store.data_api.data_list_of_cadets_at_event_with_club_dinghies.read_dict_of_cadets_and_club_dinghies_at_event, event_id=event.id)


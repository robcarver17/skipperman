from typing import List

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.club_dinghies import ClubDinghy

from app.objects.composed.people_at_event_with_club_dinghies import (
    DictOfPeopleAndClubDinghiesAtEvent,
)
from app.objects.day_selectors import Day

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
    return object_store.get(
        object_store.data_api.data_list_of_cadets_at_event_with_club_dinghies.is_a_club_dinghy_allocated_for_cadet_on_any_day_at_event,
        event_id=event.id,
        cadet_id=cadet.id,
    )


def get_dict_of_cadets_and_club_dinghies_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfPeopleAndClubDinghiesAtEvent:
    return object_store.get(
        object_store.data_api.data_list_of_cadets_at_event_with_club_dinghies.read_dict_of_cadets_and_club_dinghies_at_event,
        event_id=event.id,
    )


def add_club_dinghy_for_cadet_on_day(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
        club_dinghy: ClubDinghy,
        day: Day
):

    interface.update(
        interface.object_store.data_api.data_list_of_cadets_at_event_with_club_dinghies.update_or_add_cadet_with_club_dinghy_on_day,
        event_id=event.id,
        day=day,
        cadet_id=cadet.id,
        club_dinghy_id=club_dinghy.id,
    )


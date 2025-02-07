from typing import List

from app.backend.registration_data.cadet_registration_data import (
    is_cadet_unavailable_on_day,
)
from app.objects.cadet_at_event_with_club_boat_with_ids import NO_CLUB_BOAT

from app.objects.cadets import Cadet, ListOfCadets

from app.data_access.store.object_definitions import (
    object_definition_for_dict_of_cadets_and_club_dinghies_at_event,
)
from app.objects.club_dinghies import no_club_dinghy
from app.objects.composed.cadets_at_event_with_club_dinghies import (
    DictOfCadetsAndClubDinghiesAtEvent,
)
from app.objects.day_selectors import Day

from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore
from app.backend.club_boats.list_of_club_dinghies import get_club_dinghy_with_name


def update_club_boat_allocation_for_cadet_at_event_on_day_if_cadet_available(
    object_store: ObjectStore, event: Event, boat_name: str, cadet: Cadet, day: Day
):
    if is_cadet_unavailable_on_day(
        object_store=object_store, event=event, cadet=cadet, day=day
    ):
        return

    dict_of_cadets_and_club_dinghies_at_event = (
        get_dict_of_cadets_and_club_dinghies_at_event(
            object_store=object_store, event=event
        )
    )
    if boat_name == no_club_dinghy.name:
        dict_of_cadets_and_club_dinghies_at_event.remove_cadet_club_boat_allocation_on_day(
            cadet=cadet, day=day
        )

    else:
        club_boat = get_club_dinghy_with_name(
            object_store=object_store, boat_name=boat_name
        )
        dict_of_cadets_and_club_dinghies_at_event.allocate_club_boat_on_day(
            cadet=cadet, day=day, club_boat=club_boat
        )

    update_dict_of_cadets_and_club_dinghies_at_event(
        object_store=object_store,
        event=event,
        dict_of_cadets_and_club_dinghies_at_event=dict_of_cadets_and_club_dinghies_at_event,
    )


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
    dict_of_cadets_and_club_dinghies_at_event = (
        get_dict_of_cadets_and_club_dinghies_at_event(
            object_store=object_store, event=event
        )
    )
    boat_allocation = (
        dict_of_cadets_and_club_dinghies_at_event.get_club_boat_allocation_for_cadet(
            cadet
        )
    )

    return len(boat_allocation) > 0


def get_dict_of_cadets_and_club_dinghies_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfCadetsAndClubDinghiesAtEvent:
    return object_store.get(
        object_definition=object_definition_for_dict_of_cadets_and_club_dinghies_at_event,
        event_id=event.id,
    )


def update_dict_of_cadets_and_club_dinghies_at_event(
    object_store: ObjectStore,
    event: Event,
    dict_of_cadets_and_club_dinghies_at_event: DictOfCadetsAndClubDinghiesAtEvent,
):
    object_store.update(
        object_definition=object_definition_for_dict_of_cadets_and_club_dinghies_at_event,
        event_id=event.id,
        new_object=dict_of_cadets_and_club_dinghies_at_event,
    )

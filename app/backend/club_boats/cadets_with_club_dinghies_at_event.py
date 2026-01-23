from typing import List

from app.backend.volunteers.list_of_volunteers import get_list_of_volunteers
from app.objects.cadets import Cadet, ListOfCadets

from app.data_access.store.object_definitions import (
    object_definition_for_dict_of_people_and_club_dinghies_at_event,
)
from app.objects.club_dinghies import no_club_dinghy
from app.objects.composed.people_at_event_with_club_dinghies import (
    DEPRECATE_DictOfPeopleAndClubDinghiesAtEvent, DictOfDaysAndClubDinghiesAtEventForPerson,
    DictOfPeopleAndClubDinghiesAtEvent,
)
from app.objects.day_selectors import Day

from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore
from app.backend.club_boats.list_of_club_dinghies import get_club_dinghy_with_name
from app.objects.volunteers import ListOfVolunteers
from app.objects.volunteers_and_cades_at_event_with_club_boat_with_ids import ListOfCadetAtEventWithIdAndClubDinghies


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
        get_dict_of_people_and_club_dinghies_at_event(
            object_store=object_store, event=event
        )
    )
    boat_allocation = dict_of_cadets_and_club_dinghies_at_event.club_dinghys_for_person(
        cadet
    )

    return len(boat_allocation) > 0


def get_dict_of_people_and_club_dinghies_at_event(
    object_store: ObjectStore, event: Event
) -> DEPRECATE_DictOfPeopleAndClubDinghiesAtEvent:
    return object_store.DEPRECATE_get(
        object_definition=object_definition_for_dict_of_people_and_club_dinghies_at_event,
        event_id=event.id,
    )

def get_dict_of_cadets_and_club_dinghies_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfPeopleAndClubDinghiesAtEvent:
    return object_store.get(object_store.data_api.data_list_of_cadets_at_event_with_club_dinghies.read_dict_of_cadets_and_club_dinghies_at_event, event_id=event.id)

def get_list_of_cadets_and_club_dinghies_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfCadetAtEventWithIdAndClubDinghies:
    return object_store.get(object_store.data_api.data_list_of_cadets_at_event_with_club_dinghies.read, event_id =event.id)


def update_dict_of_people_and_club_dinghies_at_event(
    object_store: ObjectStore,
    event: Event,
    dict_of_cadets_and_club_dinghies_at_event: DEPRECATE_DictOfPeopleAndClubDinghiesAtEvent,
):
    object_store.DEPRECATE_update(
        object_definition=object_definition_for_dict_of_people_and_club_dinghies_at_event,
        event_id=event.id,
        new_object=dict_of_cadets_and_club_dinghies_at_event,
    )

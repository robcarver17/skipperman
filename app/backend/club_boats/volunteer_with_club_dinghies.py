from typing import List

from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.club_dinghies import ClubDinghy
from app.objects.composed.people_at_event_with_club_dinghies import (
    DictOfPeopleAndClubDinghiesAtEvent,
)
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.volunteers import ListOfVolunteers, Volunteer


def get_dict_of_volunteers_and_club_dinghies_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfPeopleAndClubDinghiesAtEvent:
    return object_store.get(
        object_store.data_api.data_list_of_volunteers_at_event_with_club_dinghies.read_dict_of_volunteers_and_club_dinghies_at_event,
        event_id=event.id,
    )


def get_list_of_volunteers_on_day_currently_allocated_to_club_dinghy(
    object_store: ObjectStore, event: Event, day: Day, club_dinghy: ClubDinghy
) -> ListOfVolunteers:
    club_dinghies = get_dict_of_volunteers_and_club_dinghies_at_event(
        object_store=object_store, event=event
    )

    return club_dinghies.list_of_volunteers_on_day_currently_allocated_to_club_dinghy(
        day=day, club_boat=club_dinghy
    )


def copy_club_dinghy_for_instructor_across_list_of_days_allow_overwrite(
    interface: abstractInterface,
    event: Event,
    list_of_days: List[Day],
    club_dinghy: ClubDinghy,
    volunteer: Volunteer,
):
    for day in list_of_days:
        allocate_club_dinghy_to_volunteer_on_day(
            interface=interface,
            event=event,
            volunteer=volunteer,
            day=day,
            club_dinghy=club_dinghy,
            allow_overwrite=True,
        )


def allocate_club_dinghy_to_volunteer_on_day(
    interface: abstractInterface,
    event: Event,
    day: Day,
    volunteer: Volunteer,
    club_dinghy: ClubDinghy,
    allow_overwrite: bool = False,
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event_with_club_dinghies.allocate_club_dinghy_to_volunteer_on_day,
        event_id=event.id,
        day=day,
        volunteer_id=volunteer.id,
        club_dinghy_id=club_dinghy.id,
        allow_overwrite=allow_overwrite,
    )


def remove_club_dinghy_from_volunteer_on_day(
    interface: abstractInterface, event: Event, day: Day, volunteer: Volunteer
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event_with_club_dinghies.remove_club_dinghy_from_volunteer_on_day,
        event_id=event.id,
        day=day,
        volunteer_id=volunteer.id,
    )

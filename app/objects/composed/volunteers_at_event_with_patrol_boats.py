from copy import copy
from dataclasses import dataclass
from typing import Dict, List

from app.objects.exceptions import MultipleMatches

from app.objects.utils import flatten

from app.objects.events import Event, ListOfEvents

from app.objects.volunteers import Volunteer, ListOfVolunteers

from app.objects.patrol_boats import PatrolBoat, ListOfPatrolBoats, no_patrol_boat

from app.objects.day_selectors import Day, DaySelector

from app.objects.patrol_boats_with_volunteers_with_id import (
    ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
    VolunteerWithIdAtEventWithPatrolBoatId,
)

empty_place_holder_for_new_boat = Volunteer(
    first_name="****placeholder", surname="****newboat"
)


@dataclass
class VolunteerPatrolBoatDay:
    volunteer: Volunteer
    day: Day
    patrol_boat: PatrolBoat

    @classmethod
    def from_volunteer_id_and_patrol_boat_id_at_event(
        cls,
        volunteer_id_and_patrol_boat_id_at_event: VolunteerWithIdAtEventWithPatrolBoatId,
        list_of_patrol_boats: ListOfPatrolBoats,
        list_of_volunteers: ListOfVolunteers,
    ):
        if volunteer_id_and_patrol_boat_id_at_event.is_empty:
            volunteer = empty_place_holder_for_new_boat
        else:
            volunteer_id = volunteer_id_and_patrol_boat_id_at_event.volunteer_id
            volunteer = list_of_volunteers.volunteer_with_id(volunteer_id)

        return cls(
            volunteer=volunteer,
            patrol_boat=list_of_patrol_boats.object_with_id(
                volunteer_id_and_patrol_boat_id_at_event.patrol_boat_id
            ),
            day=volunteer_id_and_patrol_boat_id_at_event.day,
        )


class PatrolBoatByDayDict(Dict[Day, PatrolBoat]):
    def boat_on_day(self, day: Day, default=no_patrol_boat) -> PatrolBoat:
        return self.get(day, default)

    def delete_patrol_boat_association(self, patrol_boat: PatrolBoat):
        for day in self.keys():
            if self[day] == patrol_boat:
                self.pop(day)

    def copy_across_boats_at_event(
        self,
        day: Day,
        volunteer_availablility_at_event: DaySelector,
        allow_overwrite: bool,
    ):
        original_boat = self.get(day)
        for day_to_copy_to in volunteer_availablility_at_event:
            existing_boat = self.on_any_patrol_boat_on_given_day(day)
            if existing_boat:
                if not allow_overwrite:
                    continue

            self[day_to_copy_to] = original_boat

    def add_boat_on_day(self, day: Day, patrol_boat: PatrolBoat):
        existing_boat = self.boat_on_day(day, None)
        if existing_boat is not None:
            raise Exception("Volunteer cannot be on more than one boat for a given day")

        self[day] = patrol_boat

    def on_any_patrol_boat_on_given_day(self, day: Day):
        return not self.not_on_patrol_boat_on_given_day(day)

    def not_on_patrol_boat_on_given_day(self, day: Day):
        boat_on_day = self.boat_on_day(day, None)

        return boat_on_day is None

    def assigned_to_boat_on_day(self, day: Day, patrol_boat: PatrolBoat):
        boat_on_day = self.boat_on_day(day, None)
        if boat_on_day is None:
            return False

        return boat_on_day == patrol_boat

    def delete_patrol_boat_on_day(self, day: Day):
        try:
            self.pop(day)
        except:
            pass

    def assigned_to_any_boat_on_any_day(self):
        return self.number_of_days_assigned_to_any_boat() > 0

    def number_of_days_assigned_to_any_boat(self):
        return len(self)

    def number_of_days_assigned_to_boat_and_day(
        self, patrol_boat: PatrolBoat, day: Day
    ):
        assigned_boat = self.boat_on_day(day, None)
        if assigned_boat is None:
            return 0
        elif assigned_boat == patrol_boat:
            return 1
        else:
            return 0

    def first_patrol_boat(self) -> PatrolBoat:
        return list(set(self.list_of_boats))[0]

    @property
    def list_of_boats(self):
        return list(self.values())


class ListOfVolunteerPatrolBoatDays(List[VolunteerPatrolBoatDay]):
    def unique_list_of_volunteers(self) -> ListOfVolunteers:
        list_of_volunteers = [
            volunteer_patrol_boat.volunteer for volunteer_patrol_boat in self
        ]
        list_of_volunteers = list(set(list_of_volunteers))
        list_of_volunteers = [
            volunteer
            for volunteer in list_of_volunteers
            if volunteer is not empty_place_holder_for_new_boat
        ]

        return ListOfVolunteers(list_of_volunteers)

    def unique_list_of_patrol_boats(self) -> ListOfPatrolBoats:
        list_of_boats = [
            volunteer_patrol_boat.patrol_boat for volunteer_patrol_boat in self
        ]

        list_of_boats = list(set(list_of_boats))

        return ListOfPatrolBoats(list_of_boats)

    @classmethod
    def from_list_of_volunteer_id_and_patrol_boat_id_at_event(
        cls,
        list_of_volunteer_ids_and_patrol_boat_id_at_event: ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
        list_of_patrol_boats: ListOfPatrolBoats,
        list_of_volunteers: ListOfVolunteers,
    ):
        return cls(
            [
                VolunteerPatrolBoatDay.from_volunteer_id_and_patrol_boat_id_at_event(
                    volunteer_id_and_patrol_boat_id_at_event=volunteer_id_and_patrol_boat_id_at_event,
                    list_of_volunteers=list_of_volunteers,
                    list_of_patrol_boats=list_of_patrol_boats,
                )
                for volunteer_id_and_patrol_boat_id_at_event in list_of_volunteer_ids_and_patrol_boat_id_at_event
            ]
        )

    def patrol_boat_dict_for_volunteer(
        self, volunteer: Volunteer
    ) -> PatrolBoatByDayDict:
        subset_for_volunteer = self.subset_for_volunteer(volunteer)
        return PatrolBoatByDayDict(
            dict(
                [
                    (patrol_boat_volunteer.day, patrol_boat_volunteer.patrol_boat)
                    for patrol_boat_volunteer in subset_for_volunteer
                ]
            )
        )

    def subset_for_volunteer(
        self, volunteer: Volunteer
    ) -> "ListOfVolunteerPatrolBoatDays":
        subset_for_volunteer = [
            patrol_boat_volunteer
            for patrol_boat_volunteer in self
            if patrol_boat_volunteer.volunteer == volunteer
        ]

        return ListOfVolunteerPatrolBoatDays(subset_for_volunteer)


class DictOfVolunteersAtEventWithPatrolBoatsByDay(Dict[Volunteer, PatrolBoatByDayDict]):
    def __init__(
        self,
        raw_dict: Dict[Volunteer, PatrolBoatByDayDict],
        event: Event,
        list_of_all_patrol_boats_at_event: ListOfPatrolBoats,
        list_of_volunteers_with_id_at_event_with_patrol_boat_id: ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
    ):
        super().__init__(raw_dict)
        self._event = event
        self._list_of_volunteers_with_id_at_event_with_patrol_boat_id = (
            list_of_volunteers_with_id_at_event_with_patrol_boat_id
        )
        self._list_of_all_patrol_boats_at_event = list_of_all_patrol_boats_at_event

    def swap_patrol_boats_for_volunteers_in_allocation(
        self,
        original_day: Day,
        original_volunteer: Volunteer,
        day_to_swap_with: Day,
        volunteer_to_swap_with: Volunteer,
    ):

        dict_of_patrol_boat_for_original_volunteer = self.patrol_boats_for_volunteer(
            original_volunteer
        )
        dict_of_patrol_boat_for_swap_volunteer = self.patrol_boats_for_volunteer(
            volunteer_to_swap_with
        )

        original_boat = copy(
            dict_of_patrol_boat_for_original_volunteer.get(original_day)
        )
        swap_boat = copy(dict_of_patrol_boat_for_swap_volunteer.get(day_to_swap_with))

        dict_of_patrol_boat_for_original_volunteer[original_day] = swap_boat
        dict_of_patrol_boat_for_swap_volunteer[day_to_swap_with] = original_boat

        self.list_of_volunteers_with_id_at_event_with_patrol_boat_id.swap_boats_for_volunteers_in_allocation(
            volunteer_id_to_swap_with=volunteer_to_swap_with.id,
            original_volunteer_id=original_volunteer.id,
            day_to_swap_with=day_to_swap_with,
            original_day=original_day,
        )

    def remove_patrol_boat_and_all_associated_volunteers_from_event(
        self, patrol_boat: PatrolBoat
    ):
        for volunteer_patrol_boats in self.values():
            volunteer_patrol_boats.delete_patrol_boat_association(patrol_boat)

        self.list_of_volunteers_with_id_at_event_with_patrol_boat_id.remove_patrol_boat_id_and_all_associated_volunteer_connections_from_event(
            patrol_boat_id=patrol_boat.id
        )

    def add_boat_to_event_with_no_allocation(self, patrol_boat: PatrolBoat):

        self.list_of_volunteers_with_id_at_event_with_patrol_boat_id.add_unallocated_boat(
            patrol_boat.id
        )

    def copy_across_boats_at_event(
        self,
        volunteer: Volunteer,
        day: Day,
        volunteer_availablility_at_event: DaySelector,
        allow_overwrite: bool,
    ):
        patrol_boats_for_volunteer = self.patrol_boats_for_volunteer(volunteer)
        patrol_boats_for_volunteer.copy_across_boats_at_event(
            volunteer_availablility_at_event=volunteer_availablility_at_event,
            day=day,
            allow_overwrite=allow_overwrite,
        )
        self.list_of_volunteers_with_id_at_event_with_patrol_boat_id.copy_across_allocation_of_boats_at_event(
            volunteer_id=volunteer.id,
            day=day,
            volunteer_availablility_at_event=volunteer_availablility_at_event,
            allow_overwrite=allow_overwrite,
        )

    def add_volunteer_with_boat(
        self, volunteer: Volunteer, patrol_boat: PatrolBoat, day: Day
    ):
        patrol_boats_for_volunteer = self.patrol_boats_for_volunteer(volunteer)
        patrol_boats_for_volunteer.add_boat_on_day(patrol_boat=patrol_boat, day=day)

        self.list_of_volunteers_with_id_at_event_with_patrol_boat_id.add_volunteer_with_boat(
            volunteer_id=volunteer.id, day=day, patrol_boat_id=patrol_boat.id
        )

    def volunteers_assigned_to_boat_on_day(
        self, patrol_boat: PatrolBoat, day: Day
    ) -> ListOfVolunteers:
        matching_volunteers = [
            volunteer
            for volunteer in self
            if self.patrol_boats_for_volunteer(volunteer).assigned_to_boat_on_day(
                day=day, patrol_boat=patrol_boat
            )
        ]

        return ListOfVolunteers(matching_volunteers)

    def volunteers_assigned_to_any_boat_on_given_day(
        self, day: Day
    ) -> ListOfVolunteers:
        matching_volunteers = [
            volunteer
            for volunteer in self
            if self.patrol_boats_for_volunteer(
                volunteer
            ).on_any_patrol_boat_on_given_day(day)
        ]

        return ListOfVolunteers(matching_volunteers)

    def list_of_unique_boats_at_event_including_unallocated(self) -> ListOfPatrolBoats:
        return self.list_of_volunteers_with_id_at_event_with_patrol_boat_id.list_of_unique_boats_at_event_including_unallocated(
            list_of_patrol_boats=self.list_of_all_patrol_boats_at_event
        )

    def list_of_volunteers_allocated_to_patrol_boat_at_event_on_any_day(
        self,
    ) -> ListOfVolunteers:
        return ListOfVolunteers(list(self.keys()))

    def drop_volunteer(self, volunteer: Volunteer):
        try:
            self.pop(volunteer)
        except:
            pass

        self.list_of_volunteers_with_id_at_event_with_patrol_boat_id.drop_volunteer(
            volunteer
        )

    def delete_patrol_boat_for_volunteer_on_day(self, volunteer: Volunteer, day: Day):
        patrol_boats_for_volunteer = self.patrol_boats_for_volunteer(volunteer)
        patrol_boats_for_volunteer.delete_patrol_boat_on_day(day)
        self.list_of_volunteers_with_id_at_event_with_patrol_boat_id.remove_volunteer_from_patrol_boat_on_day_at_event(
            volunteer_id=volunteer.id, day=day
        )

    def patrol_boats_for_volunteer(self, volunteer: Volunteer):
        return self.get(volunteer, PatrolBoatByDayDict({}))

    def number_of_volunteers_and_boats_assigned_to_boat_and_day(
        self, patrol_boat: PatrolBoat, day: Day
    ) -> int:
        return sum(
            [
                patrol_boat_by_day_dict.number_of_days_assigned_to_boat_and_day(
                    patrol_boat=patrol_boat, day=day
                )
                for patrol_boat_by_day_dict in self.values()
            ]
        )

    @property
    def list_of_volunteers_with_id_at_event_with_patrol_boat_id(
        self,
    ) -> ListOfVolunteersWithIdAtEventWithPatrolBoatsId:
        return self._list_of_volunteers_with_id_at_event_with_patrol_boat_id

    @property
    def event(self) -> Event:
        return self._event

    @property
    def list_of_all_patrol_boats_at_event(self) -> ListOfPatrolBoats:
        return self._list_of_all_patrol_boats_at_event


def compose_dict_of_patrol_boats_by_day_for_volunteer_at_event(
    event_id: str,
    list_of_events: ListOfEvents,
    list_of_volunteers: ListOfVolunteers,
    list_of_patrol_boats: ListOfPatrolBoats,
    list_of_volunteers_with_id_at_event_with_patrol_boat_id: ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
) -> DictOfVolunteersAtEventWithPatrolBoatsByDay:
    event = list_of_events.object_with_id(event_id)

    list_of_volunteer_patrol_boat_days = ListOfVolunteerPatrolBoatDays.from_list_of_volunteer_id_and_patrol_boat_id_at_event(
        list_of_volunteer_ids_and_patrol_boat_id_at_event=list_of_volunteers_with_id_at_event_with_patrol_boat_id,
        list_of_volunteers=list_of_volunteers,
        list_of_patrol_boats=list_of_patrol_boats,
    )

    unique_list_of_volunteers = (
        list_of_volunteer_patrol_boat_days.unique_list_of_volunteers()
    )
    unique_list_of_patrol_boats_at_event = (
        list_of_volunteer_patrol_boat_days.unique_list_of_patrol_boats()
    )

    raw_dict = dict(
        [
            (
                volunteer,
                list_of_volunteer_patrol_boat_days.patrol_boat_dict_for_volunteer(
                    volunteer
                ),
            )
            for volunteer in unique_list_of_volunteers
        ]
    )

    return DictOfVolunteersAtEventWithPatrolBoatsByDay(
        raw_dict=raw_dict,
        event=event,
        list_of_volunteers_with_id_at_event_with_patrol_boat_id=list_of_volunteers_with_id_at_event_with_patrol_boat_id,
        list_of_all_patrol_boats_at_event=unique_list_of_patrol_boats_at_event,
    )

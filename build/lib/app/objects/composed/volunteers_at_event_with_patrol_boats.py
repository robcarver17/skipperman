from dataclasses import dataclass
from typing import Dict, List

from app.objects.utilities.exceptions import arg_not_passed

from app.objects.utilities.utils import flatten

from app.objects.volunteers import Volunteer, ListOfVolunteers

from app.objects.patrol_boats import (
    PatrolBoat,
    ListOfPatrolBoats,
    no_patrol_boat,
    ListOfPatrolBoatLabelsAtEvents,
    get_location_for_boat,
)

from app.objects.day_selectors import Day


class PatrolBoatByDayDict(Dict[Day, PatrolBoat]):
    def boat_on_day(self, day: Day, default=arg_not_passed) -> PatrolBoat:
        if default is arg_not_passed:
            default = no_patrol_boat

        return self.get(day, default)

    def on_any_patrol_boat_on_given_day(self, day: Day):
        return not self.not_on_patrol_boat_on_given_day(day)

    def not_on_patrol_boat_on_given_day(self, day: Day):
        boat_on_day = self.boat_on_day(day, no_patrol_boat)

        not_on_boat = boat_on_day == no_patrol_boat

        return not_on_boat

    def assigned_to_boat_on_day(self, day: Day, patrol_boat: PatrolBoat):
        boat_on_day = self.boat_on_day(day, no_patrol_boat)
        if boat_on_day is no_patrol_boat:
            return False

        return boat_on_day == patrol_boat

    def assigned_to_specific_boat_on_any_day(self, patrol_boat: PatrolBoat):
        return patrol_boat.name in self.list_of_boats.list_of_names()

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
        return ListOfPatrolBoats(list(self.values()))


class DictOfVolunteersAtEventWithPatrolBoatsByDay(Dict[Volunteer, PatrolBoatByDayDict]):
    def get_dict_of_patrol_boats_with_locations(self):
        all_boats = self.list_of_unique_boats_at_event_including_unallocated()
        boats_with_locations = dict(
            [
                (patrol_boat, get_location_for_boat(patrol_boat))
                for patrol_boat in all_boats
            ]
        )

        return boats_with_locations

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
        all_boats = [item.list_of_boats for item in self.values()]
        all_boats = list(set(flatten(all_boats)))

        return ListOfPatrolBoats(all_boats)

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
                for patrol_boat_by_day_dict in self.list_of_patrol_boat_dicts_for_each_volunteer
            ]
        )

    @property
    def list_of_volunteers_with_patrol_boats(self) -> ListOfVolunteers:
        return ListOfVolunteers(list(self.keys()))

    @property
    def list_of_patrol_boat_dicts_for_each_volunteer(self) -> List[PatrolBoatByDayDict]:
        return list(self.values())


class DictOfLabelsForEventAndBoat(Dict[Day, str]):
    def label_for_day(self, day: Day, default=""):
        return self.get(day, default)


class DictOfLabelsForEvent(Dict[PatrolBoat, DictOfLabelsForEventAndBoat]):
    @classmethod
    def from_list_of_patrol_boat_labels_with_ids_for_event(
        cls,
        list_of_patrol_boat_labels_with_ids: ListOfPatrolBoatLabelsAtEvents,
        list_of_patrol_boats: ListOfPatrolBoats,
    ):
        new_dict = {}
        for raw_list_item in list_of_patrol_boat_labels_with_ids:
            boat_id = raw_list_item.boat_id
            day = raw_list_item.day
            label = raw_list_item.label

            boat = list_of_patrol_boats.boat_given_id(boat_id)
            dict_for_boat = new_dict.get(boat, DictOfLabelsForEventAndBoat())
            dict_for_boat[day] = label

            new_dict[boat] = dict_for_boat

        return cls(new_dict)

    def label_for_boat_at_event_on_day(
        self, day: Day, patrol_boat: PatrolBoat, default=""
    ) -> str:
        return self.labels_for_boat(patrol_boat).label_for_day(day, default=default)

    def labels_for_boat(self, patrol_boat: PatrolBoat) -> DictOfLabelsForEventAndBoat:
        return self.get(patrol_boat, DictOfLabelsForEventAndBoat())

    def unique_set_of_labels_at_event(self, day: Day) -> List[str]:
        return list(set(self.labels_for_day(day)))

    def labels_for_day(self, day: Day) -> List[str]:
        list_of_labels = [
            labels_for_boat.label_for_day(day, "")
            for labels_for_boat in list(self.values())
        ]
        list_of_labels = [label for label in list_of_labels if label is not ""]

        return list_of_labels


@dataclass
class BoatDayVolunteer:
    boat: PatrolBoat
    day: Day
    volunteer: Volunteer


NO_ADDITION_TO_MAKE = "No addition to make"


class ListOfBoatDayVolunteer(list):
    def __init__(self, input: List[BoatDayVolunteer]):
        super().__init__(input)

    def remove_no_additions(self):
        return ListOfBoatDayVolunteer(
            [bdv for bdv in self if not bdv is NO_ADDITION_TO_MAKE]
        )

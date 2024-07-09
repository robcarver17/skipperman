from dataclasses import dataclass
from typing import List

from app.objects.constants import missing_data, arg_not_passed
from app.objects.events import Event
from app.objects.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
)
from app.objects.generic_objects import GenericSkipperManObject, GenericSkipperManObjectWithIds
from app.objects.utils import make_id_as_int_str
from app.objects.day_selectors import Day, DaySelector


@dataclass
class PatrolBoat(GenericSkipperManObjectWithIds):
    name: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    @classmethod
    def from_dict_of_str(cls, dict_with_str):
        return cls(
            name=dict_with_str["name"], id=make_id_as_int_str(dict_with_str["id"])
        )


class ListOfPatrolBoats(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return PatrolBoat

    def delete_given_name(self, patrol_boat_name: str):
        idx = self.idx_given_name(patrol_boat_name)
        if idx is missing_data:
            raise Exception(
                "Can't find patrol boat with name to delete %s" % patrol_boat_name
            )
        self.pop(idx)

    def id_given_name(self, patrol_boat_name: str) -> str:
        boat = self.boat_given_name(patrol_boat_name)
        return boat.id

    def boat_given_name(self, patrol_boat_name: str) -> PatrolBoat:
        matching = [item for item in self if item.name == patrol_boat_name]

        if len(matching) == 0:
            return missing_data
        elif len(matching) > 1:
            raise Exception(
                "Found more than one patrol boat with same name should be impossible"
            )

        return matching[0]

    def idx_given_name(self, patrol_boat_name: str) -> int:
        boat = self.boat_given_name(patrol_boat_name)
        return self.index(boat)

    def add(self, patrol_boat_name: str):
        patrol_boat = PatrolBoat(name=patrol_boat_name)
        try:
            assert patrol_boat_name not in self.list_of_names()
        except:
            raise Exception(
                "Can't add duplicate patrol boat %s already exists" % patrol_boat_name
            )
        patrol_boat.id = self.next_id()

        self.append(patrol_boat)

    def list_of_names(self):
        return [patrol_boat.name for patrol_boat in self]


EMPTY_VOLUNTEER_ID = "NONE"
ARBITRARY_DAY = Day.Monday


@dataclass
class VolunteerAtEventWithPatrolBoat(GenericSkipperManObject):
    volunteer_id: str
    patrol_boat_id: str
    day: Day

    @classmethod
    def from_dict_of_str(cls, dict_with_str):
        volunteer_id = dict_with_str["volunteer_id"]
        patrol_boat_id = dict_with_str["patrol_boat_id"]
        day = dict_with_str["day"]
        if volunteer_id == EMPTY_VOLUNTEER_ID:
            return cls.create_unallocated_boat(make_id_as_int_str(patrol_boat_id))
        else:
            return cls(
                volunteer_id=make_id_as_int_str(volunteer_id),
                patrol_boat_id=make_id_as_int_str(patrol_boat_id),
                day=Day[day],
            )

    @classmethod
    def create_unallocated_boat(cls, patrol_boat_id: str):
        return cls(
            volunteer_id=EMPTY_VOLUNTEER_ID,
            patrol_boat_id=patrol_boat_id,
            day=ARBITRARY_DAY,
        )

    @property
    def is_empty(self):
        return self.volunteer_id == EMPTY_VOLUNTEER_ID


class ListOfVolunteersAtEventWithPatrolBoats(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return VolunteerAtEventWithPatrolBoat

    def swap_boats_for_volunteers_in_allocation(
        self,
        original_day: Day,
        original_volunteer_id: str,
        day_to_swap_with: Day,
        volunteer_id_to_swap_with: str,
    ):
        original_boat_id = self.which_boat_id_is_volunteer_on_today(
            volunteer_id=original_volunteer_id, day=original_day
        )
        swapping_boat_id = self.which_boat_id_is_volunteer_on_today(
            volunteer_id=volunteer_id_to_swap_with, day=day_to_swap_with
        )

        self.remove_volunteer_from_patrol_boat_on_day_at_event(
            volunteer_id=original_volunteer_id, day=original_day
        )
        self.remove_volunteer_from_patrol_boat_on_day_at_event(
            volunteer_id=volunteer_id_to_swap_with, day=day_to_swap_with
        )
        self.add_volunteer_with_boat(
            volunteer_id=original_volunteer_id,
            day=original_day,
            patrol_boat_id=swapping_boat_id,
        )
        self.add_volunteer_with_boat(
            volunteer_id=volunteer_id_to_swap_with,
            day=day_to_swap_with,
            patrol_boat_id=original_boat_id,
        )

    def copy_across_allocation_of_boats_at_event(
        self,
        volunteer_id: str,
        day: Day,
        volunteer_availablility_at_event: DaySelector,
        allow_overwrite: bool = True,
    ):
        current_boat_id = self.which_boat_id_is_volunteer_on_today(
            volunteer_id=volunteer_id, day=day
        )
        if current_boat_id is missing_data:
            raise Exception(
                "Can't copy %s on day %s as not allocated" % (volunteer_id, day.name)
            )

        for other_day in volunteer_availablility_at_event.days_available():
            if other_day == day:
                continue
            already_allocated = self.is_volunteer_already_on_a_boat_on_day(
                volunteer_id=volunteer_id, day=other_day
            )
            if already_allocated:
                if allow_overwrite:
                    self.remove_volunteer_from_patrol_boat_on_day_at_event(
                        volunteer_id=volunteer_id, day=other_day
                    )
                    self.add_volunteer_with_boat(
                        volunteer_id=volunteer_id,
                        patrol_boat_id=current_boat_id,
                        day=other_day,
                    )
                else:
                    continue
            else:
                self.add_volunteer_with_boat(
                    volunteer_id=volunteer_id,
                    patrol_boat_id=current_boat_id,
                    day=other_day,
                )

    def volunteer_has_at_least_one_allocated_boat_which_matches_others(
        self, volunteer_id: str
    ) -> bool:
        all_items = self.list_of_all_items_excluding_unallocated()
        list_of_boat_allocations = [
            item.patrol_boat_id
            for item in all_items
            if item.volunteer_id == volunteer_id
        ]

        if len(list_of_boat_allocations) == 0:
            return False

        return list_of_boat_allocations.count(list_of_boat_allocations[0]) == len(
            list_of_boat_allocations
        )

    def volunteer_has_at_least_one_allocated_boat_and_empty_spaces_to_fill(
        self, volunteer_id: str, volunteer_availablility_at_event: DaySelector
    ) -> bool:
        all_items = self.list_of_all_items_excluding_unallocated()
        list_of_boat_allocations = [
            item.patrol_boat_id
            for item in all_items
            if item.volunteer_id == volunteer_id
        ]
        number_of_days_available_at_event = len(
            volunteer_availablility_at_event.days_available()
        )
        number_of_allocated_days = len(list_of_boat_allocations)
        empty_spaces = number_of_days_available_at_event - number_of_allocated_days

        at_least_one_boat = number_of_allocated_days > 0
        has_empty_spaces = empty_spaces > 0

        return at_least_one_boat and has_empty_spaces

    def volunteer_is_on_same_boat_for_all_days(
        self, volunteer_id: str, event: Event
    ) -> bool:
        all_items = self.list_of_all_items_excluding_unallocated()
        list_of_boat_allocations = [
            item.patrol_boat_id
            for item in all_items
            if item.volunteer_id == volunteer_id
        ]
        number_of_days_in_event = event.duration
        number_of_allocated_days = len(list_of_boat_allocations)
        unique_boats = set(list_of_boat_allocations)

        allocated_for_all_days = number_of_allocated_days == number_of_days_in_event
        on_one_boat_entire_event = len(unique_boats) == 1

        return allocated_for_all_days and on_one_boat_entire_event

    def list_of_all_volunteer_ids_at_event(self) -> List[str]:
        all_items = self.list_of_all_items_excluding_unallocated()
        list_of_ids = [item.volunteer_id for item in all_items]
        return list_of_ids

    def list_of_volunteer_ids_assigned_to_any_boat_on_day(self, day: Day) -> List[str]:
        all_items = self.list_of_all_items_excluding_unallocated()
        list_of_ids = [item.volunteer_id for item in all_items if item.day == day]
        return list_of_ids

    def list_of_volunteer_ids_assigned_to_boat_and_day(
        self, patrol_boat: PatrolBoat, day: Day
    ) -> List[str]:
        all_items = self.list_of_all_items_excluding_unallocated()
        list_of_ids = [
            item.volunteer_id
            for item in all_items
            if item.patrol_boat_id == patrol_boat.id and item.day == day
        ]
        return list_of_ids

    def remove_patrol_boat_id_and_all_associated_volunteer_connections_from_event(
        self, patrol_boat_id: str
    ):
        for item in self:
            if item.patrol_boat_id == patrol_boat_id:
                self.remove(item)

    def add_unallocated_boat(self, patrol_boat_id: str):
        self.append(
            VolunteerAtEventWithPatrolBoat.create_unallocated_boat(
                patrol_boat_id=patrol_boat_id
            )
        )

    def remove_volunteer_from_patrol_boat_on_day_at_event(
        self, volunteer_id: str, day: Day
    ):
        for item in self:
            if item.volunteer_id == volunteer_id and item.day == day:
                self.remove(item)

    def add_volunteer_with_boat(self, volunteer_id: str, patrol_boat_id: str, day: Day):
        if self.is_volunteer_already_on_a_boat_on_day(
            volunteer_id=volunteer_id, day=day
        ):
            raise Exception("Volunteer cannot be on more than one boat for a given day")

        self.append(
            VolunteerAtEventWithPatrolBoat(
                volunteer_id=volunteer_id, patrol_boat_id=patrol_boat_id, day=day
            )
        )

    def is_volunteer_already_on_a_boat_on_day(
        self, volunteer_id: str, day: Day
    ) -> bool:
        matches = [
            item
            for item in self
            if item.volunteer_id == volunteer_id and item.day == day
        ]

        return len(matches) > 0

    def which_boat_id_is_volunteer_on_today(self, volunteer_id: str, day: Day) -> str:
        matches = [
            item
            for item in self
            if item.volunteer_id == volunteer_id and item.day == day
        ]
        if len(matches) == 0:
            return missing_data
        elif len(matches) > 1:
            raise Exception(
                "Volunteer %s day %s is on more than one boat at event shouldn't be possible!"
                % (volunteer_id, day.name)
            )

        return matches[0].patrol_boat_id

    def list_of_unique_boats_at_event_including_unallocated(
        self, list_of_patrol_boats: ListOfPatrolBoats
    ):
        ## sorted according to order of list of patrol boats
        list_of_boat_ids_at_event_including_unallocated = (
            self.list_of_unique_boat_ids_at_event_including_unallocated()
        )
        list_of_boats = [
            boat
            for boat in list_of_patrol_boats
            if make_id_as_int_str(boat.id)
            in list_of_boat_ids_at_event_including_unallocated
        ]

        return ListOfPatrolBoats(list_of_boats)

    def list_of_unique_boat_ids_at_event_including_unallocated(self) -> List[str]:
        all_ids = self.list_of_boat_ids_at_event_including_unallocated()
        return list(set(all_ids))

    def list_of_boat_ids_at_event_including_unallocated(self) -> List[str]:
        all_ids = [item.patrol_boat_id for item in self]
        return all_ids

    def list_of_all_items_excluding_unallocated(self):
        return ListOfVolunteersAtEventWithPatrolBoats(
            [item for item in self if not item.is_empty]
        )

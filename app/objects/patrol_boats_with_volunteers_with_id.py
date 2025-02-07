from dataclasses import dataclass
from typing import List

from app.objects.volunteers import Volunteer

from app.objects.day_selectors import Day, DaySelector
from app.objects.events import Event
from app.objects.exceptions import missing_data, MissingData, MultipleMatches, arg_not_passed
from app.objects.generic_list_of_objects import GenericListOfObjectsWithIds
from app.objects.generic_objects import GenericSkipperManObject
from app.objects.patrol_boats import PatrolBoat, ListOfPatrolBoats
from app.objects.utils import make_id_as_int_str


EMPTY_VOLUNTEER_ID = "NONE" ## DO NOT CHANGE
ARBITRARY_DAY = Day.Monday


@dataclass
class VolunteerWithIdAtEventWithPatrolBoatId(GenericSkipperManObject):
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


class ListOfVolunteersWithIdAtEventWithPatrolBoatsId(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return VolunteerWithIdAtEventWithPatrolBoatId

    def drop_volunteer(self, volunteer: Volunteer):
        for item in self:
            if item.volunteer_id == volunteer.id:
                self.remove(item)

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

    def remove_patrol_boat_id_and_all_associated_volunteer_connections_from_event(
        self, patrol_boat_id: str
    ):
        for item in self:
            if item.patrol_boat_id == patrol_boat_id:
                self.remove(item)

    def add_unallocated_boat(self, patrol_boat_id: str):
        self.append(
            VolunteerWithIdAtEventWithPatrolBoatId.create_unallocated_boat(
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
            VolunteerWithIdAtEventWithPatrolBoatId(
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

    def which_boat_id_is_volunteer_on_today(self, volunteer_id: str, day: Day, default = arg_not_passed) -> str:
        matches = [
            item
            for item in self
            if item.volunteer_id == volunteer_id and item.day == day
        ]
        if len(matches) == 0:
            if default is arg_not_passed:
                raise MissingData
            else:
                return default

        elif len(matches) > 1:
            raise MultipleMatches(
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

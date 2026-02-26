from dataclasses import dataclass
from typing import List

from app.objects.volunteers import Volunteer

from app.objects.day_selectors import Day, DaySelector
from app.objects.utilities.exceptions import (
    missing_data,
    MissingData,
    arg_not_passed,
)
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    get_unique_object_with_multiple_attr_in_list,
)
from app.objects.utilities.generic_objects import GenericSkipperManObject
from app.objects.patrol_boats import ListOfPatrolBoats, no_patrol_boat
from app.objects.utilities.transform_data import make_id_as_int_str

OLD_EMPTY_VOLUNTEER_ID = "NONE"  ## DO NOT CHANGE
EMPTY_VOLUNTEER_ID = "-999219"
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

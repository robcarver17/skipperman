from dataclasses import dataclass
from typing import List

from app.objects.volunteers_at_event import VolunteerEventData
from app.objects.primtive_with_id.volunteer_roles_and_groups import RoleAndGroup

from app.objects.primtive_with_id.patrol_boats import PatrolBoat, VolunteerWithIdAtEventWithPatrolBoatId
from app.objects.primtive_with_id.volunteers import Volunteer, ListOfVolunteers

from app.objects.generic_list_of_objects import (
    GenericListOfObjects
)
from app.objects.generic_objects import GenericSkipperManObject

from app.objects.day_selectors import Day


@dataclass
class DEPRECATE_VolunteerAtEventWithPatrolBoat(GenericSkipperManObject):
    volunteer: Volunteer
    day: Day
    patrol_boat: PatrolBoat

    @classmethod
    def from_volunteer_with_id_and_patrol_boat_id(cls, volunteer_with_id_at_event_with_patrol_boat_id: VolunteerWithIdAtEventWithPatrolBoatId,
                                                  volunteer: Volunteer,
                                                  patrol_boat: PatrolBoat):

        return cls(volunteer=volunteer, patrol_boat=patrol_boat, day=volunteer_with_id_at_event_with_patrol_boat_id.day)


class DEPRECATE_ListOfVolunteersAtEventWithPatrolBoats(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return DEPRECATE_VolunteerAtEventWithPatrolBoat

    def list_of_volunteers(self) -> ListOfVolunteers:
        return ListOfVolunteers([volunteer_at_event_with_boat.volunteer for volunteer_at_event_with_boat in self])

    def unique_list_of_volunteers(self)-> ListOfVolunteers:
        list_of_volunteers = self.list_of_volunteers()

        return ListOfVolunteers(list(set(list_of_volunteers)))

    def list_of_volunteers_and_boats_assigned_to_boat_and_day(self, patrol_boat: PatrolBoat, day: Day) -> 'DEPRECATE_ListOfVolunteersAtEventWithPatrolBoats':
        return DEPRECATE_ListOfVolunteersAtEventWithPatrolBoats([volunteer_at_event_with_boat for volunteer_at_event_with_boat in self
                                                                 if volunteer_at_event_with_boat.day == day and
                                                                 volunteer_at_event_with_boat.patrol_boat == patrol_boat])


from app.objects.primtive_with_id.volunteer_skills import SkillsDict

@dataclass
class VolunteerAtEventWithPatrolBoatAndRoleOnDay:
    volunteer: Volunteer
    day: Day
    patrol_boat: PatrolBoat
    role_and_group: RoleAndGroup

class ListOfVolunteersAtEventWithPatrolBoatAndRole(List[VolunteerAtEventWithPatrolBoatAndRoleOnDay]):
    pass
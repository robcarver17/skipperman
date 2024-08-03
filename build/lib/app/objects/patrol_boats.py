from dataclasses import dataclass
from typing import List, Dict

from app.objects.volunteers_in_roles import RoleAndGroupByDayDict, VolunteerAtEventWithSkillsAndRoles

from app.objects.volunteers_at_event import VolunteerEventData

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

class PatrolBoatByDayDict(Dict[Day, PatrolBoat]):
    pass

@dataclass
class VolunteerAtEventWithSkillsAndRolesAndPatrolBoats:
    volunteer: Volunteer
    skills: SkillsDict
    volunteer_event_data: VolunteerEventData
    role_and_group_by_day: RoleAndGroupByDayDict
    patrol_boat_by_day: PatrolBoatByDayDict

    def __hash__(self):
        return hash(self.volunteer.id)

    def has_pb2_qualification(self):
        return self.skills.can_drive_safety_boat

    def assigned_to_any_boat_on_any_day(self):
        return len(self.patrol_boat_by_day)>0

    def assigned_to_boat_on_day(self,  patrol_boat: PatrolBoat, day: Day) -> int:
        patrol_boat_on_day = self.patrol_boat_by_day.get(day, patrol_boat.create_empty())
        return patrol_boat == patrol_boat_on_day

    def has_role_on_day(self, day: Day, role: str) -> bool:
        return self.role_and_group_by_day.has_role_on_day(day=day, role=role)

    @classmethod
    def from_volunteer_at_event_with_skills_and_roles(cls, volunteer_at_event_with_skills_and_roles:VolunteerAtEventWithSkillsAndRoles,
                                                      patrol_boat_by_day: PatrolBoatByDayDict):
        return cls(
            volunteer=volunteer_at_event_with_skills_and_roles.volunteer,
            skills=volunteer_at_event_with_skills_and_roles.skills,
            volunteer_event_data=volunteer_at_event_with_skills_and_roles.volunteer_event_data,
            role_and_group_by_day=volunteer_at_event_with_skills_and_roles.role_and_group_by_day,
            patrol_boat_by_day=patrol_boat_by_day
        )

class ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats(List[VolunteerAtEventWithSkillsAndRolesAndPatrolBoats]):
    def number_of_volunteers_and_boats_assigned_to_boat_and_day(self,  patrol_boat: PatrolBoat, day: Day) -> int:
        return len(self.assigned_to_boat_on_day(patrol_boat=patrol_boat, day=day))

    def assigned_to_any_boat_on_any_day(self) -> 'ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats':

        return ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats([
            volunteer_at_event_with_skills_and_roles_and_boats for volunteer_at_event_with_skills_and_roles_and_boats in
            self if volunteer_at_event_with_skills_and_roles_and_boats.assigned_to_any_boat_on_any_day()
        ])

    def assigned_to_boat_on_day(self,  patrol_boat: PatrolBoat, day: Day) -> 'ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats':
        return ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats([
            volunteer_at_event_with_skills_and_roles_and_boats for volunteer_at_event_with_skills_and_roles_and_boats in
            self if volunteer_at_event_with_skills_and_roles_and_boats.assigned_to_boat_on_day(patrol_boat=patrol_boat, day=day)
        ])

    def list_of_volunteer_ids(self) -> List[str]:
        return [
            volunteer_at_event_with_skills_and_roles_and_boats.volunteer.id for volunteer_at_event_with_skills_and_roles_and_boats in self
        ]

    def volunteers_with_pb2(self):
        return ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats([
            volunteer_at_event_with_skills_and_roles_and_boats for volunteer_at_event_with_skills_and_roles_and_boats in
            self if volunteer_at_event_with_skills_and_roles_and_boats.has_pb2_qualification()
        ])

    def has_volunteer_role(self, role: str, day: Day):
        return ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats([
            volunteer_at_event_with_skills_and_roles_and_boats for volunteer_at_event_with_skills_and_roles_and_boats in
            self if volunteer_at_event_with_skills_and_roles_and_boats.has_role_on_day(day=day, role=role)
        ])

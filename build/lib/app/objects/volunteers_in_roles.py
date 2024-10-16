from dataclasses import dataclass
from typing import Dict, List

from app.objects.composed.volunteers_with_skills import SkillsDict

from app.objects.volunteer_roles_and_groups_with_id import NO_ROLE_SET, VolunteerWithIdInRoleAtEvent, RoleAndGroupDEPRECATE
from app.objects.volunteers import Volunteer

from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject
from app.objects.groups import Group, unallocated_group
from app.objects.day_selectors import Day
from app.objects_OLD.volunteers_in_roles import VolunteerEventData_DEPRECATE, VolunteerAtEventWithSkills_DEPRECATE


## must match below


@dataclass
class VolunteerInRoleAtEventWithTeamName(GenericSkipperManObject):
    volunteer_in_role_at_event: VolunteerWithIdInRoleAtEvent
    team_name: str


## Not saved, used purely for sorting purposes


FILTER_ALL = "All"
FILTER_AVAILABLE = "Available"
FILTER_UNALLOC_AVAILABLE = "Unallocated+Available"
FILTER_ALLOC_AVAILABLE = "Allocated+Available"
FILTER_UNAVAILABLE = "Unavailable"
FILTER_OPTIONS = [
    FILTER_ALL,
    FILTER_AVAILABLE,
    FILTER_UNALLOC_AVAILABLE,
    FILTER_ALLOC_AVAILABLE,
    FILTER_UNAVAILABLE,
]


@dataclass
class DEPRECATE_VolunteerWithRoleAtEvent(GenericSkipperManObject):
    volunteer: Volunteer
    day: Day
    role: str = NO_ROLE_SET
    group: Group = unallocated_group

    @classmethod
    def from_volunteer_with_id_in_role_at_event(cls, volunteer_with_id_in_role_at_event: VolunteerWithIdInRoleAtEvent,
                                                volunteer: Volunteer):

        return cls(
            volunteer=volunteer,
            day=volunteer_with_id_in_role_at_event.day,
            role=volunteer_with_id_in_role_at_event.role,
            group=volunteer_with_id_in_role_at_event.group
        )

class DEPRECATE_ListOfVolunteersWithRoleAtEvent(GenericListOfObjects):
    def _object_class_contained(self):
        return DEPRECATE_VolunteerWithRoleAtEvent

class RoleAndGroupByDayDict(Dict[Day, RoleAndGroupDEPRECATE]):
    def has_role_on_day(self, day: Day, role: str) -> bool:
        return self.role_and_group_on_day(day).role==role

    def role_and_group_on_day(self, day: Day) -> RoleAndGroupDEPRECATE:
        return self.get(day, RoleAndGroupDEPRECATE.create_empty())

@dataclass
class VolunteerAtEventWithSkillsAndRoles:
    volunteer: Volunteer
    skills: SkillsDict
    volunteer_event_data: VolunteerEventData_DEPRECATE
    role_and_group_by_day: RoleAndGroupByDayDict

    @classmethod
    def from_volunteer_at_event_with_skills(cls, volunteer_at_event_with_skills: VolunteerAtEventWithSkills_DEPRECATE, role_and_group_by_day: RoleAndGroupByDayDict):
        return cls(
            volunteer=volunteer_at_event_with_skills.volunteer,
            skills=volunteer_at_event_with_skills.skills_dict,
            volunteer_event_data=volunteer_at_event_with_skills.volunteer_event_data,
            role_and_group_by_day=role_and_group_by_day
        )

class ListOfVolunteersAtEventWithSkillsAndRoles(List[VolunteerAtEventWithSkillsAndRoles]):
    pass
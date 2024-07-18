from dataclasses import dataclass

from app.objects.primtive_with_id.volunteer_roles_and_groups import NO_ROLE_SET, VolunteerWithIdInRoleAtEvent
from app.objects.primtive_with_id.volunteers import Volunteer

from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject
from app.objects.primtive_with_id.groups import Group, GROUP_UNALLOCATED
from app.objects.day_selectors import Day


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
class VolunteerWithRoleAtEvent(GenericSkipperManObject):
    volunteer: Volunteer
    day: Day
    role: str = NO_ROLE_SET
    group: Group = GROUP_UNALLOCATED

    @classmethod
    def from_volunteer_with_id_in_role_at_event(cls, volunteer_with_id_in_role_at_event: VolunteerWithIdInRoleAtEvent,
                                                volunteer: Volunteer):

        return cls(
            volunteer=volunteer,
            day=volunteer_with_id_in_role_at_event.day,
            role=volunteer_with_id_in_role_at_event.role,
            group=volunteer_with_id_in_role_at_event.group
        )

class ListOfVolunteersWithRoleAtEvent(GenericListOfObjects):
    def _object_class_contained(self):
        return VolunteerWithRoleAtEvent



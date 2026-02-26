
from dataclasses import dataclass


from app.objects.roles_and_teams import Team, no_role_allocated_id

from app.objects.day_selectors import Day
from app.objects.utilities.exceptions import  arg_not_passed
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjects,
    get_unique_object_with_multiple_attr_in_list,
)
from app.objects.utilities.generic_objects import GenericSkipperManObject
from app.objects.groups import Group, unallocated_group, unallocated_group_id


DAY_KEY = "day"
GROUP_KEY = "group"


@dataclass
class TeamAndGroup(GenericSkipperManObject):
    team: Team
    group: Group = unallocated_group

    def __repr__(self):
        if self.group == unallocated_group:
            return self.team.name
        else:
            return "%s (%s)" % (self.team.name, self.group.name)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash("%s_%s" % (self.team.name, self.group.name))


@dataclass
class VolunteerWithIdInRoleAtEvent(GenericSkipperManObject):
    volunteer_id: str
    day: Day
    group_id: str = unallocated_group_id
    role_id: str = no_role_allocated_id


class ListOfVolunteersWithIdInRoleAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return VolunteerWithIdInRoleAtEvent


    def member_matching_volunteer_id_and_day(
        self, volunteer_id: str, day: Day, default=arg_not_passed
    ) -> VolunteerWithIdInRoleAtEvent:
        return get_unique_object_with_multiple_attr_in_list(
            some_list=self,
            dict_of_attributes={"volunteer_id": volunteer_id, "day": day},
            default=default,
        )

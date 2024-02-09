from copy import copy
from dataclasses import dataclass
from typing import List
from statistics import mode

from app.data_access.configuration.configuration import VOLUNTEER_ROLES, VOLUNTEERS_REQUIRING_GROUP
from app.objects.generic import GenericSkipperManObject, get_class_instance_from_str_dict, GenericListOfObjects, _transform_class_dict_into_str_dict
from app.objects.groups import Group, GROUP_UNALLOCATED, index_group
from app.objects.day_selectors import Day
from app.objects.constants import missing_data

NO_ROLE_SET = "No role allocated"

## must match below
DAY_KEY = "day"
GROUP_KEY = "group"
@dataclass
class VolunteerInRoleAtEvent(GenericSkipperManObject):
    volunteer_id: str
    day: Day
    role: str = NO_ROLE_SET
    group: Group = GROUP_UNALLOCATED

    @property
    def role_and_group(self):
        return RoleAndGroup(role=self.role, group=self.group)

    @property
    def requires_group(self):
        return self.role in VOLUNTEERS_REQUIRING_GROUP

    @property
    def no_role_set(self) -> bool:
        return self.role == NO_ROLE_SET

def index_of_role(role: str):
    combined_roles = VOLUNTEER_ROLES+[NO_ROLE_SET]
    return combined_roles.index(role)

## Not saved, used purely for sorting purposes
@dataclass
class RoleAndGroup(GenericSkipperManObject):
    role: str = NO_ROLE_SET
    group: Group = GROUP_UNALLOCATED

    def __repr__(self):
        if self.group == GROUP_UNALLOCATED:
            return self.role
        else:
            return "%s (%s)" % (self.role, self.group)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash("%s_%s" % (self.role, self.group.group_name))

    def __lt__(self, other):
        role_index = index_of_role(self.role)
        other_role_index = index_of_role(other.role)

        if role_index < other_role_index:
            return True
        elif role_index > other_role_index:
            return False

        group_index = index_group(self.group)
        other_group_index = index_group(other.group)

        return group_index<other_group_index

class ListOfVolunteersInRoleAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return VolunteerInRoleAtEvent

    def list_of_roles_and_groups_at_event_for_day(self, day: Day) -> List[RoleAndGroup]:
        return [volunteer_with_role.role_and_group for volunteer_with_role in self if volunteer_with_role.day == day]

    def most_common_role_at_event_for_volunteer(self, volunteer_id: str) -> str:
        ## crazy that mode works with strings
        all_roles = self.all_roles_for_a_specific_volunteer(volunteer_id)
        if len(all_roles)==0:
            return NO_ROLE_SET

        return mode(all_roles)

    def all_roles_for_a_specific_volunteer(self, volunteer_id: str)-> List[str]:
        list_of_matches = [volunteer_with_role for volunteer_with_role in self if volunteer_with_role.volunteer_id == volunteer_id]

        return [volunteer_with_role.role for volunteer_with_role in list_of_matches]

    def copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(self,
        volunteer_id:str,
        day: Day,
        list_of_all_days: List[Day]
    ):
        volunteer_with_role = self.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_id,
            day=day
        )
        print("Copying %s" % str(volunteer_with_role))
        new_list_of_days = copy(list_of_all_days)
        new_list_of_days.remove(day)

        for other_day in new_list_of_days:

            self.replace_or_add_volunteer_in_group_on_day_with_copy(day=other_day,
                                                                    volunteer_in_role_at_event=volunteer_with_role)

    def member_matching_volunteer_id_and_day(self, volunteer_id: str, day: Day, return_empty_if_missing: bool = True):
        list_of_matches = [volunteer_with_role for volunteer_with_role in self if volunteer_with_role.volunteer_id == volunteer_id
                           and volunteer_with_role.day==day]

        if len(list_of_matches)==0:
            if return_empty_if_missing:
                return VolunteerInRoleAtEvent(volunteer_id=volunteer_id, day=day)
            else:
                return missing_data
        if len(list_of_matches)==1:
            return list_of_matches[0]
        elif len(list_of_matches)>0:
            raise Exception("Cannot have more than one volunteer for a given day")

    def update_volunteer_in_role_on_day(self, volunteer_in_role_at_event: VolunteerInRoleAtEvent,
                                        new_role: str):

        if new_role==NO_ROLE_SET:
            self.delete_volunteer_in_role_at_event_on_day(volunteer_in_role_at_event)
        else:
            self.update_volunteer_in_role_on_day_to_actual_role(volunteer_in_role_at_event=volunteer_in_role_at_event,
                                                                new_role=new_role)

    def delete_volunteer_in_role_at_event_on_day(self, volunteer_in_role_at_event: VolunteerInRoleAtEvent):
        existing_member = self.member_matching_volunteer_id_and_day(volunteer_id=volunteer_in_role_at_event.volunteer_id,
                                                           day=volunteer_in_role_at_event.day, return_empty_if_missing=False)

        if existing_member is missing_data:
            pass
        else:
            self.remove(existing_member)

    def update_volunteer_in_role_on_day_to_actual_role(self, volunteer_in_role_at_event: VolunteerInRoleAtEvent,
                                        new_role: str):
        existing_member = self.member_matching_volunteer_id_and_day(volunteer_id=volunteer_in_role_at_event.volunteer_id,
                                                           day=volunteer_in_role_at_event.day, return_empty_if_missing=False)

        if existing_member is missing_data:
            volunteer_in_role_at_event.role= new_role
            self.append(volunteer_in_role_at_event)
        else:
            existing_member.role = new_role


    def update_volunteer_in_group_on_day(self, volunteer_in_role_at_event: VolunteerInRoleAtEvent,
                                        new_group: str):
        existing_member = self.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_in_role_at_event.volunteer_id,
            day=volunteer_in_role_at_event.day, return_empty_if_missing=False)

        if existing_member is missing_data:
            volunteer_in_role_at_event.group = new_group
            self.append(volunteer_in_role_at_event)
        else:
            existing_member.group = new_group

    def replace_or_add_volunteer_in_group_on_day_with_copy(self, day: Day, volunteer_in_role_at_event: VolunteerInRoleAtEvent):
        existing_member = self.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_in_role_at_event.volunteer_id,
            day=day, return_empty_if_missing=False)

        if existing_member is missing_data:
            copied_volunteer_in_role_at_event = copy(volunteer_in_role_at_event)
            copied_volunteer_in_role_at_event.day = day
            self.append(copied_volunteer_in_role_at_event)
        else:
            existing_member.group = volunteer_in_role_at_event.group
            existing_member.role = volunteer_in_role_at_event.role

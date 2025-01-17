from copy import copy
from dataclasses import dataclass
from typing import List

from app.objects.roles_and_teams import Team

from app.objects.day_selectors import Day
from app.objects.exceptions import missing_data
from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject
from app.objects.groups import Group, unallocated_group
from app.objects.volunteers import Volunteer

NO_GROUP_SET = "No group set"
DAY_KEY = "day"
GROUP_KEY = "group"


NO_ROLE_SET = "No role allocated"


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

    def __lt__(self, other):
        raise Exception("Can't properly sort role/group yet")


@dataclass
class VolunteerWithIdInRoleAtEvent(GenericSkipperManObject):
    volunteer_id: str
    day: Day
    group_id: str = NO_GROUP_SET
    role_id: str = NO_ROLE_SET


class ListOfVolunteersWithIdInRoleAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return VolunteerWithIdInRoleAtEvent

    def update_role_and_group_at_event_for_volunteer_on_all_days_when_available(
        self,
        volunteer: Volunteer,
        group_id: str,
        role_id: str,
        list_of_days_available: List[Day],
    ):
        for day in list_of_days_available:
            self.update_volunteer_in_role_on_day(
                volunteer=volunteer, day=day, new_role_id=role_id
            )
            self.update_volunteer_in_group_on_day(
                volunteer=volunteer, day=day, new_group_id=group_id
            )

    def drop_volunteer(self, volunteer: Volunteer):
        for item in self:
            if item.volunteer_id == volunteer.id:
                self.remove(item)

    def swap_roles_and_groups_for_volunteers_in_allocation(
        self,
        original_day: Day,
        original_volunteer_id: str,
        day_to_swap_with: Day,
        volunteer_id_to_swap_with: str,
    ):
        original_volunteer = self.member_matching_volunteer_id_and_day(
            volunteer_id=original_volunteer_id,
            day=original_day,
            return_empty_if_missing=False,
        )

        volunteer_to_swap_with = self.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_id_to_swap_with,
            day=day_to_swap_with,
            return_empty_if_missing=False,
        )

        if original_volunteer is missing_data or volunteer_to_swap_with is missing_data:
            raise Exception("can't swap non existent volunteers!")

        original_volunteer_group_id = copy(original_volunteer.group_id)
        original_volunteer_role_id = copy(original_volunteer.role_id)

        volunteer_to_swap_with_group_id = copy(volunteer_to_swap_with.group_id)
        volunteer_to_swap_with_role_id = copy(volunteer_to_swap_with.role_id)

        original_volunteer.role_id = volunteer_to_swap_with_role_id
        original_volunteer.group_id = volunteer_to_swap_with_group_id

        volunteer_to_swap_with.role_id = original_volunteer_role_id
        volunteer_to_swap_with.group_id = original_volunteer_group_id

    def copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        self,
        volunteer_id: str,
        day: Day,
        list_of_all_days: List[Day],
        allow_replacement: bool = True,
    ):
        volunteer_with_role = self.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_id, day=day
        )
        new_list_of_days = copy(list_of_all_days)
        new_list_of_days.remove(day)

        for other_day in new_list_of_days:
            print("day %s" % str(other_day))
            self.replace_or_add_volunteer_in_group_on_day_with_copy(
                day=other_day,
                volunteer_in_role_at_event=volunteer_with_role,
                allow_replacement=allow_replacement,
            )

    def member_matching_volunteer_id_and_day(
        self, volunteer_id: str, day: Day, return_empty_if_missing: bool = True
    ) -> VolunteerWithIdInRoleAtEvent:
        list_of_matches = [
            volunteer_with_role
            for volunteer_with_role in self
            if volunteer_with_role.volunteer_id == volunteer_id
            and volunteer_with_role.day == day
        ]

        if len(list_of_matches) == 0:
            if return_empty_if_missing:
                return VolunteerWithIdInRoleAtEvent(volunteer_id=volunteer_id, day=day)
            else:
                return missing_data
        if len(list_of_matches) == 1:
            return list_of_matches[0]
        elif len(list_of_matches) > 0:
            raise Exception("Cannot have more than one volunteer for a given day")

    def update_volunteer_in_role_on_day(
        self, volunteer: Volunteer, day: Day, new_role_id: str
    ):
        if new_role_id == NO_ROLE_SET:
            self.delete_volunteer_in_role_at_event_on_day(volunteer=volunteer, day=day)
        else:
            self.update_volunteer_in_role_on_day_to_actual_role(
                volunteer_id=volunteer.id, day=day, new_role_id=new_role_id
            )

    def delete_volunteer_in_role_at_event_on_day(self, volunteer: Volunteer, day: Day):
        existing_member = self.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer.id,
            day=day,
            return_empty_if_missing=False,
        )

        if existing_member is missing_data:
            pass
        else:
            self.remove(existing_member)

    def update_volunteer_in_role_on_day_to_actual_role(
        self, volunteer_id: str, day: Day, new_role_id: str
    ):
        existing_member = self.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_id,
            day=day,
            return_empty_if_missing=False,
        )

        if existing_member is missing_data:
            volunteer_in_role_at_event = VolunteerWithIdInRoleAtEvent(
                volunteer_id=volunteer_id,
                day=day,
                role_id=new_role_id,
                group_id=unallocated_group.id,
            )
            self.append(volunteer_in_role_at_event)
        else:
            existing_member.role_id = new_role_id

    def update_volunteer_in_group_on_day(
        self, volunteer: Volunteer, day: Day, new_group_id: str
    ):
        existing_member = self.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer.id,
            day=day,
            return_empty_if_missing=False,
        )

        if existing_member is missing_data:
            raise Exception("Can't update group if role not already set")
        else:
            existing_member.group_id = new_group_id

    def replace_or_add_volunteer_in_group_on_day_with_copy(
        self,
        day: Day,
        volunteer_in_role_at_event: VolunteerWithIdInRoleAtEvent,
        allow_replacement: bool = True,
    ):
        existing_member = self.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_in_role_at_event.volunteer_id,
            day=day,
            return_empty_if_missing=False,
        )

        print("existing %s" % str(existing_member))
        if existing_member is missing_data:
            print("missing, copying to new")
            copied_volunteer_in_role_at_event = copy(volunteer_in_role_at_event)
            copied_volunteer_in_role_at_event.day = day
            self.append(copied_volunteer_in_role_at_event)
        else:
            current_role_id = existing_member.role_id
            no_role_set = current_role_id == NO_ROLE_SET
            print("no role set %s" % str(no_role_set))
            if allow_replacement or no_role_set:
                print("overwriting role")
                existing_member.role_id = volunteer_in_role_at_event.role_id

            current_group_id = existing_member.group_id
            no_group_set = current_group_id == NO_GROUP_SET
            print("no group set %s" % str(no_group_set))
            if no_group_set or allow_replacement:
                print("overwriting group")
                existing_member.group_id = volunteer_in_role_at_event.group_id

        print("existing after %s" % str(existing_member))

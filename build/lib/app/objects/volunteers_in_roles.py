from copy import copy
from dataclasses import dataclass
from typing import List, Dict
from statistics import mode

from app.objects.volunteers import Volunteer

from app.data_access.configuration.configuration import (
    VOLUNTEERS_REQUIRING_GROUP,
    VOLUNTEERS_REQUIRING_BOATS,
    VOLUNTEER_ROLES,
    VOLUNTEER_TEAMS,
    SI_ROLE,
    INSTRUCTOR_TEAM,
    VOLUNTEER_SKILL_DICT,
)
from app.objects.generic import GenericSkipperManObject, GenericListOfObjects
from app.objects.groups import Group, GROUP_UNALLOCATED, index_group
from app.objects.day_selectors import Day
from app.objects.constants import missing_data

NO_ROLE_SET = "No role allocated"


## must match below
DAY_KEY = "day"
GROUP_KEY = "group"


def get_list_of_volunteer_teams():
    return list(VOLUNTEER_TEAMS.keys())


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
    def first_team_and_group(self):
        return TeamAndGroup(team=self.list_of_teams[0], group=self.group)

    @property
    def requires_group(self):
        return self.role in VOLUNTEERS_REQUIRING_GROUP

    @property
    def requires_boat(self):
        return self.role in VOLUNTEERS_REQUIRING_BOATS

    @property
    def no_role_set(self) -> bool:
        return self.role == NO_ROLE_SET

    @property
    def list_of_teams(self) -> List[str]:
        return teams_given_role(self.role)

    def senior_instructor(self) -> bool:
        return self.role == SI_ROLE

    def in_instructor_team(self):
        return self.role in INSTRUCTOR_TEAM

    def on_lake(self):
        if not self.group.is_unallocated:
            if self.group.is_lake_training():
                return True

        if "lake" in self.role.lower():
            return True

        return False

    def is_qualified_for_role(self, dict_of_skills: Dict[str, bool]) -> bool:
        return is_qualified_for_role(role=self.role, dict_of_skills=dict_of_skills)


def is_qualified_for_role(role: str, dict_of_skills: Dict[str, bool]) -> bool:
    skills_required = VOLUNTEER_SKILL_DICT.get(role, [])
    for skill_needed in skills_required:
        has_skill = dict_of_skills.get(skill_needed, False)
        if not has_skill:
            return False

    return True


def teams_given_role(role: str, teams: dict = VOLUNTEER_TEAMS) -> List[str]:
    if role == NO_ROLE_SET:
        return [NO_ROLE_SET]
    all_teams = [
        team_name for team_name, team_members in teams.items() if role in team_members
    ]

    if len(all_teams) == 0:
        return [NO_ROLE_SET]

    return all_teams


def index_of_role(role: str):
    combined_roles = VOLUNTEER_ROLES + [NO_ROLE_SET]
    return combined_roles.index(role)


def index_of_team(role: str):
    combined_teams = VOLUNTEER_TEAMS + [NO_ROLE_SET]
    return combined_teams.index(role)


@dataclass
class VolunteerInRoleAtEventWithTeamName(GenericSkipperManObject):
    volunteer_in_role_at_event: VolunteerInRoleAtEvent
    team_name: str


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

        return group_index < other_group_index

    @property
    def missing(self):
        return self.role == NO_ROLE_SET and self.group == GROUP_UNALLOCATED


@dataclass
class TeamAndGroup(GenericSkipperManObject):
    team: str = NO_ROLE_SET
    group: Group = GROUP_UNALLOCATED

    def __repr__(self):
        if self.group == GROUP_UNALLOCATED:
            return self.team
        else:
            return "%s (%s)" % (self.team, self.group)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash("%s_%s" % (self.team, self.group.group_name))

    def __lt__(self, other):
        team_index = index_of_team(self.team)
        other_team_index = index_of_team(other.team)

        if team_index < other_team_index:
            return True
        elif team_index > other_team_index:
            return False

        group_index = index_group(self.group)
        other_group_index = index_group(other.group)

        return group_index < other_group_index


class ListOfVolunteersInRoleAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return VolunteerInRoleAtEvent

    def list_if_volunteer_id_in_list_of_ids(
        self, list_of_ids: List[str]
    ) -> "ListOfVolunteersInRoleAtEvent":
        return ListOfVolunteersInRoleAtEvent(
            [
                volunteer_in_role
                for volunteer_in_role in self
                if volunteer_in_role.volunteer_id in list_of_ids
            ]
        )

    def swap_roles_for_volunteers_in_allocation(
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
        original_volunteer_role = copy(original_volunteer.role)

        volunteer_to_swap_with = self.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_id_to_swap_with,
            day=day_to_swap_with,
            return_empty_if_missing=False,
        )
        volunteer_to_swap_with_role = copy(volunteer_to_swap_with.role)

        self.update_volunteer_in_role_on_day_to_actual_role(
            original_volunteer, new_role=volunteer_to_swap_with_role
        )
        self.update_volunteer_in_role_on_day_to_actual_role(
            volunteer_to_swap_with, new_role=original_volunteer_role
        )

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
        original_volunteer_group_name = copy(original_volunteer.group.group_name)
        original_volunteer_role = copy(original_volunteer.role)

        volunteer_to_swap_with = self.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_id_to_swap_with,
            day=day_to_swap_with,
            return_empty_if_missing=False,
        )
        volunteer_to_swap_with_group_name = copy(
            volunteer_to_swap_with.group.group_name
        )
        volunteer_to_swap_with_role = copy(volunteer_to_swap_with.role)

        self.update_volunteer_in_role_on_day_to_actual_role(
            original_volunteer, new_role=volunteer_to_swap_with_role
        )
        self.update_volunteer_in_group_on_day(
            original_volunteer, new_group=volunteer_to_swap_with_group_name
        )

        self.update_volunteer_in_role_on_day_to_actual_role(
            volunteer_to_swap_with, new_role=original_volunteer_role
        )
        self.update_volunteer_in_group_on_day(
            volunteer_to_swap_with, new_group=original_volunteer_group_name
        )

    def list_of_volunteer_ids_in_boat_related_role_on_day(self, day: Day) -> List[str]:
        return list(
            set(
                [
                    item.volunteer_id
                    for item in self
                    if item.day == day and item.requires_boat
                ]
            )
        )

    def list_of_volunteer_ids_in_boat_related_role_on_any_day(self) -> List[str]:
        return list(set([item.volunteer_id for item in self if item.requires_boat]))

    def list_of_roles_and_groups_at_event_for_day(self, day: Day) -> List[RoleAndGroup]:
        return [
            volunteer_with_role.role_and_group
            for volunteer_with_role in self
            if volunteer_with_role.day == day
        ]

    def list_of_first_teams_and_groups_at_event_for_day(
        self, day: Day
    ) -> List[RoleAndGroup]:
        return [
            volunteer_with_role.first_team_and_group
            for volunteer_with_role in self
            if volunteer_with_role.day == day
        ]

    def most_common_role_and_group_at_event_for_volunteer(
        self, volunteer: Volunteer
    ) -> RoleAndGroup:
        ## crazy that mode works with strings
        all_roles = self.all_roles_and_groups_for_a_specific_volunteer(volunteer)
        if len(all_roles) == 0:
            return RoleAndGroup()

        return mode(all_roles)

    def all_roles_and_groups_for_a_specific_volunteer(
        self, volunteer: Volunteer
    ) -> List[RoleAndGroup]:
        list_of_matches = [
            volunteer_with_role
            for volunteer_with_role in self
            if volunteer_with_role.volunteer_id == volunteer.id
        ]

        return [
            volunteer_with_role.role_and_group
            for volunteer_with_role in list_of_matches
        ]

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
            self.replace_or_add_volunteer_in_group_on_day_with_copy(
                day=other_day,
                volunteer_in_role_at_event=volunteer_with_role,
                allow_replacement=allow_replacement,
            )

    def member_matching_volunteer_id_and_day(
        self, volunteer_id: str, day: Day, return_empty_if_missing: bool = True
    ) -> VolunteerInRoleAtEvent:
        list_of_matches = [
            volunteer_with_role
            for volunteer_with_role in self
            if volunteer_with_role.volunteer_id == volunteer_id
            and volunteer_with_role.day == day
        ]

        if len(list_of_matches) == 0:
            if return_empty_if_missing:
                return VolunteerInRoleAtEvent(volunteer_id=volunteer_id, day=day)
            else:
                return missing_data
        if len(list_of_matches) == 1:
            return list_of_matches[0]
        elif len(list_of_matches) > 0:
            raise Exception("Cannot have more than one volunteer for a given day")

    def update_volunteer_in_role_on_day(
        self, volunteer_in_role_at_event: VolunteerInRoleAtEvent, new_role: str
    ):
        if new_role == NO_ROLE_SET:
            self.delete_volunteer_in_role_at_event_on_day(volunteer_in_role_at_event)
        else:
            self.update_volunteer_in_role_on_day_to_actual_role(
                volunteer_in_role_at_event=volunteer_in_role_at_event, new_role=new_role
            )

    def delete_volunteer_in_role_at_event_on_day(
        self, volunteer_in_role_at_event: VolunteerInRoleAtEvent
    ):
        existing_member = self.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_in_role_at_event.volunteer_id,
            day=volunteer_in_role_at_event.day,
            return_empty_if_missing=False,
        )

        if existing_member is missing_data:
            pass
        else:
            self.remove(existing_member)

    def update_volunteer_in_role_on_day_to_actual_role(
        self, volunteer_in_role_at_event: VolunteerInRoleAtEvent, new_role: str
    ):
        existing_member = self.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_in_role_at_event.volunteer_id,
            day=volunteer_in_role_at_event.day,
            return_empty_if_missing=False,
        )

        if existing_member is missing_data:
            volunteer_in_role_at_event.role = new_role
            self.append(volunteer_in_role_at_event)
        else:
            existing_member.role = new_role

    def update_volunteer_in_group_on_day(
        self, volunteer_in_role_at_event: VolunteerInRoleAtEvent, new_group: Group
    ):
        existing_member = self.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_in_role_at_event.volunteer_id,
            day=volunteer_in_role_at_event.day,
            return_empty_if_missing=False,
        )

        if existing_member is missing_data:
            volunteer_in_role_at_event.group = new_group
            self.append(volunteer_in_role_at_event)
        else:
            existing_member.group = new_group

    def replace_or_add_volunteer_in_group_on_day_with_copy(
        self,
        day: Day,
        volunteer_in_role_at_event: VolunteerInRoleAtEvent,
        allow_replacement: bool = True,
    ):
        existing_member = self.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_in_role_at_event.volunteer_id,
            day=day,
            return_empty_if_missing=False,
        )

        if existing_member is missing_data:
            copied_volunteer_in_role_at_event = copy(volunteer_in_role_at_event)
            copied_volunteer_in_role_at_event.day = day
            self.append(copied_volunteer_in_role_at_event)
        else:
            current_role = existing_member.role
            no_role_set = current_role == NO_ROLE_SET
            if allow_replacement or no_role_set:
                existing_member.role = volunteer_in_role_at_event.role

            current_group = existing_member.group
            no_group_set = current_group.is_unallocated
            if no_group_set or allow_replacement:
                existing_member.group = volunteer_in_role_at_event.group


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
class TargetForRoleAtEvent(GenericSkipperManObject):
    role: str
    target: int


class ListOfTargetForRoleAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return TargetForRoleAtEvent

    def get_target_for_role(self, role: str) -> int:
        matching_item = self._get_target_object_for_role_at_event(role=role)
        if matching_item is missing_data:
            return 0

        return matching_item.target

    def set_target_for_role(self, role: str, target: int):
        matching_item = self._get_target_object_for_role_at_event(role=role)
        if matching_item is missing_data:
            self._add_target_for_role(role=role, target=target)
        else:
            self._update_target_for_role(role=role, target=target)

    def _add_target_for_role(self, role: str, target: int):
        self.append(TargetForRoleAtEvent(role=role, target=target))

    def _update_target_for_role(self, role: str, target):
        matching_item = self._get_target_object_for_role_at_event(role=role)
        matching_item.target = target

    def _get_target_object_for_role_at_event(self, role: str):
        matching = [item for item in self if item.role == role]
        if len(matching) > 1:
            raise Exception("Can't have duplicates")
        if len(matching) == 0:
            return missing_data

        return matching[0]

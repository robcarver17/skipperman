from dataclasses import dataclass
from typing import Dict, List, Union

from app.objects.utilities.exceptions import arg_not_passed
from app.objects.roles_and_teams import Team, role_location_lake
from app.objects.utilities.utils import most_common, flatten


from app.objects.volunteers import Volunteer, ListOfVolunteers

from app.objects.day_selectors import Day

from app.objects.groups import Group, ListOfGroups, unallocated_group

from app.objects.composed.volunteer_roles import (
    RoleWithSkills,
    no_role_set,
    ListOfRolesWithSkills,
)
from app.objects.composed.roles_and_teams import ListOfTeamsAndIndices
from app.objects.roles_and_teams import ListOfRolesWithSkillIds


@dataclass
class VolunteerWithRoleGroupAndTeamAtEvent:
    volunteer: Volunteer
    day: Day
    role: RoleWithSkills
    group: Group
    list_of_team_and_index: ListOfTeamsAndIndices

    def in_instructor_team(self):
        return self.list_of_team_and_index.in_instructor_team()


@dataclass
class RoleAndGroup:
    role: RoleWithSkills = no_role_set
    group: Group = unallocated_group

    def __repr__(self):
        if self.group == unallocated_group:
            return self.role.name
        else:
            return "%s (%s)" % (self.role.name, self.group.name)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash("%s_%s" % (self.role.name, self.group.name))

    @property
    def is_unallocated(self):
        return self == unallocated_role_and_group

    def index_for_sort(
        self,
        list_of_groups: ListOfGroups,
        list_of_roles: Union[ListOfRolesWithSkills, ListOfRolesWithSkillIds],
    ):
        ## sort by role first, do names in case objects slightly different
        role_index = list_of_roles.list_of_names().index(self.role.name)
        group_index = list_of_groups.list_of_names().index(self.group.name)

        return (
            1000 * role_index
        ) + group_index  ## fine as long as less than 1000 groups

    @classmethod
    def create_empty(cls):
        return cls(role=no_role_set, group=unallocated_group)

    @property
    def is_si(self) -> bool:
        return self.role.is_si()


unallocated_role_and_group = RoleAndGroup.create_empty()


class ListOfRolesAndGroups(List[RoleAndGroup]):
    def sorted(
        self,
        list_of_groups: ListOfGroups,
        list_of_roles: Union[ListOfRolesWithSkills, ListOfRolesWithSkillIds],
    ) -> "ListOfRolesAndGroups":
        as_tuple_list = [
            (
                item,
                item.index_for_sort(
                    list_of_roles=list_of_roles, list_of_groups=list_of_groups
                ),
            )
            for item in self
        ]
        sorted_by_indices = sorted(as_tuple_list, key=lambda tup: tup[1])
        as_single_sorted_list = [item[0] for item in sorted_by_indices]

        return ListOfRolesAndGroups(as_single_sorted_list)


@dataclass
class RoleAndGroupAndTeam:
    role: RoleWithSkills
    group: Group
    list_of_team_and_index: ListOfTeamsAndIndices

    def __repr__(self):
        if self.group.is_unallocated:
            return self.role.name
        else:
            return "%s (%s)" % (self.role.name, self.group.name)

    def __hash__(self):
        return hash(str(self.role) + "___" + str(self.group))

    def not_in_team(self):
        return len(self.list_of_team_and_index) == 0

    def role_and_group(self):
        return RoleAndGroup(role=self.role, group=self.group)

    def matches_team_and_group(self, team: Team, group: Group):
        return self.group == group and self.list_of_team_and_index.contains_team(team)

    @classmethod
    def create_unallocated(cls):
        return cls(
            no_role_set,
            unallocated_group,
            list_of_team_and_index=ListOfTeamsAndIndices([]),
        )

    @property
    def is_unallocated(self):
        return self == unallocated_role_and_group_and_team

    @property
    def is_si(self) -> bool:
        return self.role.is_si()


class ListOfRolesAndGroupsAndTeams(List[RoleAndGroupAndTeam]):
    @property
    def list_of_groups(self) -> ListOfGroups:
        return ListOfGroups([role_and_group.group for role_and_group in self])

    @property
    def list_of_roles(self) -> List[RoleWithSkills]:
        return [role_and_group.role for role_and_group in self]

    @property
    def list_of_teams(self) -> List[Team]:
        teams_list = [
            role_and_group.list_of_team_and_index.list_of_teams
            for role_and_group in self
        ]
        teams_list = flatten(teams_list)

        return list(set(teams_list))


unallocated_role_and_group_and_team = RoleAndGroupAndTeam.create_unallocated()


class DictOfDaysRolesAndGroups(Dict[Day, RoleAndGroup]):
    def subset_where_role_in_list_of_roles(self, list_of_roles: List[RoleWithSkills]):
        list_of_ids = [role.id for role in list_of_roles]
        return DictOfDaysRolesAndGroups(
            [
                (day, role_and_group)
                for day, role_and_group in self.items()
                if role_and_group.role.id in list_of_ids
            ]
        )

    def most_common(self) -> RoleAndGroup:
        roles_and_groups = list(self.values())

        return most_common(roles_and_groups, RoleAndGroup.create_empty())

    def role_and_group_on_day(
        self, day: Day, default=unallocated_role_and_group
    ) -> RoleAndGroup:
        return self.get(day, default)

    def contains_si(self) -> bool:
        return any([role_and_group.is_si for role_and_group in list(self.values())])


class DictOfDaysRolesAndGroupsAndTeams(Dict[Day, RoleAndGroupAndTeam]):
    def role_and_group_and_team_on_day(
        self, day: Day, default=arg_not_passed
    ) -> RoleAndGroupAndTeam:
        if default is arg_not_passed:
            default = RoleAndGroupAndTeam.create_unallocated()

        return self.get(day, default)

    def role_and_group_on_day(self, day: Day) -> RoleAndGroup:
        role_and_group_and_team = self.role_and_group_and_team_on_day(day)
        return role_and_group_and_team.role_and_group()

    def most_common_role_and_groups(self) -> RoleAndGroupAndTeam:
        return most_common(
            self.list_of_roles_and_groups,
            default=RoleAndGroupAndTeam.create_unallocated(),
        )

    def list_of_groups(self) -> ListOfGroups:
        return self.list_of_roles_and_groups.list_of_groups

    def list_of_roles(self) -> List[RoleWithSkills]:
        return self.list_of_roles_and_groups.list_of_roles

    def list_of_teams(self) -> List[Team]:
        return self.list_of_roles_and_groups.list_of_teams

    @property
    def list_of_roles_and_groups(self) -> ListOfRolesAndGroupsAndTeams:
        return ListOfRolesAndGroupsAndTeams(list(self.values()))

    def contains_si(self) -> bool:
        return any(
            [role_and_group.is_si for role_and_group in self.list_of_roles_and_groups]
        )

    def subset_where_role_in_list_of_roles(self, list_of_roles: List[RoleWithSkills]):
        return DictOfDaysRolesAndGroupsAndTeams(
            [
                (day, role_and_group)
                for day, role_and_group in self.items()
                if role_and_group.role in list_of_roles
            ]
        )

    def is_on_lake_during_event(self) -> bool:
        list_of_teams = self.list_of_teams()
        lake_teams = [
            team
            for team in list_of_teams
            if team.location_for_cadet_warning == role_location_lake
        ]

        return len(lake_teams) > 0


class ListOfVolunteersWithRoleAtEvent(List[VolunteerWithRoleGroupAndTeamAtEvent]):
    def unique_list_of_volunteers(self) -> ListOfVolunteers:
        return ListOfVolunteers(
            list(set([volunteer_with_role.volunteer for volunteer_with_role in self]))
        )

    def dict_of_days_roles_and_groups_for_volunteer(
        self, volunteer: Volunteer
    ) -> DictOfDaysRolesAndGroupsAndTeams:
        subset_for_volunteer = self.subset_for_volunteer(volunteer)
        return DictOfDaysRolesAndGroupsAndTeams(
            dict(
                [
                    (
                        volunteer_with_role.day,
                        RoleAndGroupAndTeam(
                            role=volunteer_with_role.role,
                            group=volunteer_with_role.group,
                            list_of_team_and_index=volunteer_with_role.list_of_team_and_index,
                        ),
                    )
                    for volunteer_with_role in subset_for_volunteer
                ]
            )
        )

    def subset_for_volunteer(self, volunteer: Volunteer):
        return ListOfVolunteersWithRoleAtEvent(
            [
                volunteer_with_role
                for volunteer_with_role in self
                if volunteer_with_role.volunteer == volunteer
            ]
        )


class DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups(
    Dict[Volunteer, DictOfDaysRolesAndGroupsAndTeams]
):
    def list_of_volunteers_with_roles_and_groups_and_teams_assigned_to_group_on_day(
        self, group: Group, day: Day
    ) -> List[VolunteerWithRoleGroupAndTeamAtEvent]:
        list_of_volunteers = []
        for volunteer, roles_for_volunteer in self.items():
            role_and_group_and_team = (
                roles_for_volunteer.role_and_group_and_team_on_day(day)
            )
            if role_and_group_and_team.group == group:
                list_of_volunteers.append(
                    VolunteerWithRoleGroupAndTeamAtEvent(
                        volunteer=volunteer,
                        role=role_and_group_and_team.role,
                        group=role_and_group_and_team.group,
                        list_of_team_and_index=role_and_group_and_team.list_of_team_and_index,
                        day=day,
                    )
                )
        return list_of_volunteers

    def list_of_volunteers_with_roles_and_groups_and_teams_doing_role_on_day(
        self, role: RoleWithSkills, day: Day
    ) -> List[VolunteerWithRoleGroupAndTeamAtEvent]:
        list_of_volunteers = []
        for volunteer, roles_for_volunteer in self.items():
            role_and_group_and_team = (
                roles_for_volunteer.role_and_group_and_team_on_day(day)
            )
            if role_and_group_and_team.role == role:
                list_of_volunteers.append(
                    VolunteerWithRoleGroupAndTeamAtEvent(
                        volunteer=volunteer,
                        role=role_and_group_and_team.role,
                        group=role_and_group_and_team.group,
                        list_of_team_and_index=role_and_group_and_team.list_of_team_and_index,
                        day=day,
                    )
                )
        return list_of_volunteers

    def count_of_volunteers_in_role_on_day(self, role: RoleWithSkills, day: Day) -> int:
        all_dicts_of_roles_and_groups = self.all_dicts_of_roles_and_groups

        sum_values = [
            1
            for dict_of_roles_for_volunteer in all_dicts_of_roles_and_groups
            if dict_of_roles_for_volunteer.role_and_group_on_day(day).role == role
        ]

        return sum(sum_values)

    @property
    def all_teams_at_event(self) -> List[Team]:
        all_teams = [
            dict_of_roles_and_group.list_of_teams()
            for dict_of_roles_and_group in self.all_dicts_of_roles_and_groups
        ]
        all_teams = flatten(all_teams)

        return list(set(all_teams))

    @property
    def all_roles_at_event(self) -> ListOfRolesWithSkills:
        all_roles_at_event = [
            dict_of_roles_and_group.list_of_roles()
            for dict_of_roles_and_group in self.all_dicts_of_roles_and_groups
        ]
        all_roles_at_event = flatten(all_roles_at_event)
        unique_list_of_roles = list(set(all_roles_at_event))

        return ListOfRolesWithSkills(unique_list_of_roles)

    def list_of_all_roles_and_groups_and_teams_for_day(
        self, day: Day
    ) -> List[RoleAndGroupAndTeam]:
        all_dicts_of_roles_and_groups = self.all_dicts_of_roles_and_groups
        return [
            dict_of_role_and_group.role_and_group_and_team_on_day(day)
            for dict_of_role_and_group in all_dicts_of_roles_and_groups
        ]

    def list_of_all_roles_and_groups_for_day(self, day: Day) -> List[RoleAndGroup]:
        all_dicts_of_roles_and_groups = self.all_dicts_of_roles_and_groups
        return [
            dict_of_role_and_group.role_and_group_on_day(day)
            for dict_of_role_and_group in all_dicts_of_roles_and_groups
        ]

    @property
    def all_dicts_of_roles_and_groups(self) -> List[DictOfDaysRolesAndGroupsAndTeams]:
        return list(self.values())

    def days_and_roles_for_volunteer(
        self, volunteer: Volunteer
    ) -> DictOfDaysRolesAndGroupsAndTeams:
        default = DictOfDaysRolesAndGroupsAndTeams()
        return self.get(volunteer, default)

    def list_of_volunteers(self) -> ListOfVolunteers:
        return ListOfVolunteers(list(self.keys()))

from dataclasses import dataclass
from typing import Dict, List, Union

from app.objects.roles_and_teams import Team, RolesWithSkillIds, role_location_lake

from app.objects.utils import most_common, flatten

from app.objects.events import ListOfEvents, Event

from app.objects.volunteer_roles_and_groups_with_id import (
    ListOfVolunteersWithIdInRoleAtEvent,
    VolunteerWithIdInRoleAtEvent,
)

from app.objects.volunteers import Volunteer, ListOfVolunteers

from app.objects.day_selectors import Day

from app.objects.groups import Group, ListOfGroups, unallocated_group

from app.objects.composed.volunteer_roles import RoleWithSkills, no_role_set
from app.objects.composed.roles_and_teams import (
    ListOfRolesWithSkills,
    DictOfTeamsWithRoles,
    ListOfTeamsAndIndices,
)
from app.objects.roles_and_teams import ListOfRolesWithSkillIds


@dataclass
class VolunteerWithRoleAtEvent:
    volunteer: Volunteer
    day: Day
    role: RoleWithSkills
    group: Group
    list_of_team_and_index: ListOfTeamsAndIndices

    @classmethod
    def from_volunteer_with_id_in_role_at_event(
        cls,
        volunteer_with_id_in_role_at_event: VolunteerWithIdInRoleAtEvent,
        list_of_volunteers: ListOfVolunteers,
        list_of_groups: ListOfGroups,
        list_of_roles_with_skills: ListOfRolesWithSkills,
        dict_of_teams_and_roles: DictOfTeamsWithRoles,
    ):
        volunteer = list_of_volunteers.volunteer_with_id(
            volunteer_with_id_in_role_at_event.volunteer_id
        )
        role = list_of_roles_with_skills.role_with_id(
            volunteer_with_id_in_role_at_event.role_id
        )
        day = volunteer_with_id_in_role_at_event.day
        group = list_of_groups.object_with_id(
            volunteer_with_id_in_role_at_event.group_id
        )
        list_of_team_and_index = (
            dict_of_teams_and_roles.list_of_teams_and_index_given_role(role)
        )

        return cls(
            volunteer=volunteer,
            role=role,
            day=day,
            group=group,
            list_of_team_and_index=list_of_team_and_index,
        )


@dataclass
class RoleAndGroup:
    role: RoleWithSkills = no_role_set
    group: Group = unallocated_group

    def __repr__(self):
        if self.group == unallocated_group:
            return self.role
        else:
            return "%s (%s)" % (self.role, self.group)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash("%s_%s" % (self.role, self.group.name))

    def index_for_sort(self,  list_of_groups: ListOfGroups, list_of_roles:Union[ListOfRolesWithSkills, ListOfRolesWithSkillIds]):
        ## sort by role first, do names in case objects slightly different
        role_index = list_of_roles.list_of_names().index(self.role.name)
        group_index = list_of_groups.list_of_names().index(self.group.name)

        return (1000*role_index) + group_index ## fine as long as less than 1000 groups

class ListOfRolesAndGroups(List[RoleAndGroup]):
    def sorted(self, list_of_groups: ListOfGroups, list_of_roles:Union[ListOfRolesWithSkills, ListOfRolesWithSkillIds]) -> 'ListOfRolesAndGroups':
        as_tuple_list = [(item, item.index_for_sort(list_of_roles=list_of_roles, list_of_groups=list_of_groups)) for item in self]
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
        return self == unallocated_role_and_group

    @property
    def is_si(self) -> bool:
        return self.role.is_si()


class ListOfRolesAndGroupsAndTeams(List[RoleAndGroupAndTeam]):
    @property
    def list_of_groups(self) -> List[Group]:
        return [role_and_group.group for role_and_group in self]

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


unallocated_role_and_group = RoleAndGroupAndTeam.create_unallocated()


class DictOfDaysRolesAndGroups(Dict[Day, RoleAndGroupAndTeam]):
    def role_and_group_and_team_on_day(self, day: Day):
        return self.get(day, RoleAndGroupAndTeam.create_unallocated())

    def role_and_group_on_day(self, day: Day) -> RoleAndGroup:
        role_and_group_and_team = self.role_and_group_and_team_on_day(day)
        return role_and_group_and_team.role_and_group()

    def most_common_role_and_groups(self) -> RoleAndGroupAndTeam:
        return most_common(
            self.list_of_roles_and_groups,
            default=RoleAndGroupAndTeam.create_unallocated(),
        )

    def list_of_groups(self) -> List[Group]:
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
        return DictOfDaysRolesAndGroups(
            [
                (day, role_and_group)
                for day, role_and_group in self.items()
                if role_and_group.role in list_of_roles
            ]
        )

    def is_on_lake_during_event(self) -> bool:
        list_of_teams = self.list_of_teams()
        lake_teams = [team for team in list_of_teams if team.location_for_cadet_warning==role_location_lake]

        return len(lake_teams)>0


class ListOfVolunteersWithRoleAtEvent(List[VolunteerWithRoleAtEvent]):
    @classmethod
    def from_list_of_volunteers_with_id_in_role_at_event(
        cls,
        list_of_volunteers_with_id_in_role_at_event: ListOfVolunteersWithIdInRoleAtEvent,
        list_of_volunteers: ListOfVolunteers,
        list_of_groups: ListOfGroups,
        list_of_roles_with_skills: ListOfRolesWithSkills,
        dict_of_teams_and_roles: DictOfTeamsWithRoles,
    ):
        return cls(
            [
                VolunteerWithRoleAtEvent.from_volunteer_with_id_in_role_at_event(
                    volunteer_with_id_in_role_at_event=volunteer_with_id_in_role_at_event,
                    list_of_groups=list_of_groups,
                    list_of_roles_with_skills=list_of_roles_with_skills,
                    list_of_volunteers=list_of_volunteers,
                    dict_of_teams_and_roles=dict_of_teams_and_roles,
                )
                for volunteer_with_id_in_role_at_event in list_of_volunteers_with_id_in_role_at_event
            ]
        )

    def unique_list_of_volunteers(self) -> ListOfVolunteers:
        return ListOfVolunteers(
            list(set([volunteer_with_role.volunteer for volunteer_with_role in self]))
        )

    def dict_of_days_roles_and_groups_for_volunteer(
        self, volunteer: Volunteer
    ) -> DictOfDaysRolesAndGroups:
        subset_for_volunteer = self.subset_for_volunteer(volunteer)
        return DictOfDaysRolesAndGroups(
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
    Dict[Volunteer, DictOfDaysRolesAndGroups]
):
    def __init__(
        self,
        raw_dict: Dict[Volunteer, DictOfDaysRolesAndGroups],
        list_of_volunteers_with_id_in_role_at_event: ListOfVolunteersWithIdInRoleAtEvent,
        event: Event,
    ):
        super().__init__(raw_dict)
        self._list_of_volunteers_with_id_in_role_at_event = (
            list_of_volunteers_with_id_in_role_at_event
        )
        self._event = event


    def count_of_volunteers_in_role_on_day(self, role: RolesWithSkillIds, day: Day) -> int:
        all_dicts_of_roles_and_groups = self.all_dicts_of_roles_and_groups

        sum_values = [1 for dict_of_roles_for_volunteer in all_dicts_of_roles_and_groups if dict_of_roles_for_volunteer.role_and_group_on_day(day).role== role]

        return sum(sum_values)

    @property
    def all_groups_at_event(self) -> List[Group]:
        all_groups = [
            dict_of_roles_and_group.list_of_groups()
            for dict_of_roles_and_group in self.all_dicts_of_roles_and_groups
        ]
        all_groups = flatten(all_groups)
        return list(set(all_groups))

    @property
    def all_teams_at_event(self) -> List[Team]:
        all_teams = [
            dict_of_roles_and_group.list_of_teams()
            for dict_of_roles_and_group in self.all_dicts_of_roles_and_groups
        ]
        all_teams = flatten(all_teams)

        return list(set(all_teams))

    @property
    def all_roles_at_event(self) -> List[RoleWithSkills]:
        all_roles = [
            dict_of_roles_and_group.list_of_roles()
            for dict_of_roles_and_group in self.all_dicts_of_roles_and_groups
        ]
        all_roles = flatten(all_roles)

        return all_roles

    def list_of_all_roles_and_groups_and_teams_for_day(
        self, day: Day
    ) -> List[RoleAndGroupAndTeam]:
        all_dicts_of_roles_and_groups = self.all_dicts_of_roles_and_groups
        return [
            dict_of_role_and_group.role_and_group_and_team_on_day(day)
            for dict_of_role_and_group in all_dicts_of_roles_and_groups
        ]

    def list_of_all_roles_and_groups_for_day(
        self, day: Day
    ) -> List[RoleAndGroup]:
        all_dicts_of_roles_and_groups = self.all_dicts_of_roles_and_groups
        return [
            dict_of_role_and_group.role_and_group_on_day(day)
            for dict_of_role_and_group in all_dicts_of_roles_and_groups
        ]

    @property
    def all_dicts_of_roles_and_groups(self) -> List[DictOfDaysRolesAndGroups]:
        return list(self.values())

    def days_and_roles_for_volunteer(self, volunteer: Volunteer):
        return self.get(volunteer, DictOfDaysRolesAndGroups())

    @property
    def list_of_volunteers_with_id_in_role_at_event(
        self,
    ) -> ListOfVolunteersWithIdInRoleAtEvent:
        return self._list_of_volunteers_with_id_in_role_at_event

    def list_of_volunteers(self) -> ListOfVolunteers:
        return ListOfVolunteers(list(self.keys()))

    @property
    def event(self) -> Event:
        return self._event


def compose_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups(
    event_id: str,
    list_of_events: ListOfEvents,
    list_of_volunteers: ListOfVolunteers,
    list_of_groups: ListOfGroups,
    list_of_roles_with_skills: ListOfRolesWithSkills,
    dict_of_teams_and_roles: DictOfTeamsWithRoles,
    list_of_volunteers_with_id_in_role_at_event: ListOfVolunteersWithIdInRoleAtEvent,
) -> DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups:
    event = list_of_events.object_with_id(event_id)
    raw_dict = compose_raw_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups(
        list_of_volunteers=list_of_volunteers,
        list_of_groups=list_of_groups,
        list_of_roles_with_skills=list_of_roles_with_skills,
        list_of_volunteers_with_id_in_role_at_event=list_of_volunteers_with_id_in_role_at_event,
        dict_of_teams_and_roles=dict_of_teams_and_roles,
    )

    return DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups(
        raw_dict=raw_dict,
        event=event,
        list_of_volunteers_with_id_in_role_at_event=list_of_volunteers_with_id_in_role_at_event,
    )


def compose_raw_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups(
    list_of_volunteers: ListOfVolunteers,
    list_of_groups: ListOfGroups,
    list_of_roles_with_skills: ListOfRolesWithSkills,
    list_of_volunteers_with_id_in_role_at_event: ListOfVolunteersWithIdInRoleAtEvent,
    dict_of_teams_and_roles: DictOfTeamsWithRoles,
) -> Dict[Volunteer, DictOfDaysRolesAndGroups]:
    list_of_volunteers_with_role_in_event = ListOfVolunteersWithRoleAtEvent.from_list_of_volunteers_with_id_in_role_at_event(
        list_of_volunteers_with_id_in_role_at_event=list_of_volunteers_with_id_in_role_at_event,
        list_of_volunteers=list_of_volunteers,
        list_of_groups=list_of_groups,
        list_of_roles_with_skills=list_of_roles_with_skills,
        dict_of_teams_and_roles=dict_of_teams_and_roles,
    )

    volunteers_at_event = (
        list_of_volunteers_with_role_in_event.unique_list_of_volunteers()
    )

    return dict(
        [
            (
                volunteer,
                list_of_volunteers_with_role_in_event.dict_of_days_roles_and_groups_for_volunteer(
                    volunteer
                ),
            )
            for volunteer in volunteers_at_event
        ]
    )

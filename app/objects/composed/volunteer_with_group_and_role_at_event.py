from copy import copy
from dataclasses import dataclass
from typing import Dict, List, Union

from app.objects.utilities.exceptions import arg_not_passed
from app.objects.roles_and_teams import Team, role_location_lake
from app.objects.utilities.utils import most_common, flatten

from app.objects.events import ListOfEvents, Event

from app.objects.volunteer_roles_and_groups_with_id import (
    ListOfVolunteersWithIdInRoleAtEvent,
    VolunteerWithIdInRoleAtEvent,
)

from app.objects.volunteers import Volunteer, ListOfVolunteers

from app.objects.day_selectors import Day, DaySelector

from app.objects.groups import Group, ListOfGroups, unallocated_group

from app.objects.composed.volunteer_roles import RoleWithSkills, no_role_set
from app.objects.composed.roles_and_teams import (
    ListOfRolesWithSkills,
    DictOfTeamsWithRoles,
    ListOfTeamsAndIndices,
)
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
        group = list_of_groups.group_with_id(
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

    def update_role_and_group(
        self, new_role: RoleWithSkills, new_group: Group = arg_not_passed
    ):
        self.role = new_role

        new_group_provided = not new_group is arg_not_passed
        if new_role.associate_sailing_group:
            if new_group_provided:
                self.group = new_group
            else:
                ## keep current group, which may be not provided
                pass

        else:
            self.group = unallocated_group

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


class DictOfDaysRolesAndGroupsAndTeams(Dict[Day, RoleAndGroupAndTeam]):
    def update_role_and_group_on_day(
        self,
        day: Day,
        new_role: RoleWithSkills,
        new_group: Group = arg_not_passed,  ### if not passed, no change
    ):
        existing_role_group_and_team = self.role_and_group_and_team_on_day(day)
        existing_role_group_and_team.update_role_and_group(
            new_role=new_role, new_group=new_group
        )
        self[day] = existing_role_group_and_team

    def update_role_and_group_at_event_for_volunteer_on_all_days_when_available(
        self, new_role_and_group: RoleAndGroupAndTeam, list_of_days_available: List[Day]
    ):
        for day in list_of_days_available:
            self[day] = new_role_and_group

    def copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        self,
        day: Day,
        list_of_all_days: List[Day],
        allow_replacement: bool = True,
    ):
        role_group_team_to_copy = self.role_and_group_and_team_on_day(day)
        for other_day in list_of_all_days:
            if day == other_day:
                continue
            existing_role_group_team = self.role_and_group_and_team_on_day(
                other_day, None
            )
            if existing_role_group_team is None or allow_replacement:
                self[other_day] = role_group_team_to_copy

    def delete_role_on_day(self, day):
        try:
            self.pop(day)
        except:
            pass

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
                VolunteerWithRoleGroupAndTeamAtEvent.from_volunteer_with_id_in_role_at_event(
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
    def __init__(
        self,
        raw_dict: Dict[Volunteer, DictOfDaysRolesAndGroupsAndTeams],
        list_of_volunteers_with_id_in_role_at_event: ListOfVolunteersWithIdInRoleAtEvent,
        event: Event,
        dict_of_teams_and_roles: DictOfTeamsWithRoles,
        list_of_groups: ListOfGroups,
        list_of_roles_with_skills: ListOfRolesWithSkills,
    ):
        super().__init__(raw_dict)
        self._list_of_volunteers_with_id_in_role_at_event = (
            list_of_volunteers_with_id_in_role_at_event
        )
        self._event = event
        self._dict_of_teams_and_roles = dict_of_teams_and_roles
        self._list_of_groups = list_of_groups

        self._list_of_roles_with_skills = list_of_roles_with_skills

    def swap_roles_and_groups_for_volunteers_in_allocation(
        self,
        original_day: Day,
        original_volunteer: Volunteer,
        day_to_swap_with: Day,
        volunteer_to_swap_with: Volunteer,
    ):
        days_and_roles_for_original_volunteer = self.days_and_roles_for_volunteer(
            original_volunteer
        )
        days_and_roles_for_swap_volunteer = self.days_and_roles_for_volunteer(
            volunteer_to_swap_with
        )
        original_volunteer_role_and_group = copy(
            days_and_roles_for_original_volunteer.role_and_group_and_team_on_day(
                original_day
            )
        )
        volunteer_to_swap_with_role_and_group = copy(
            days_and_roles_for_swap_volunteer.role_and_group_and_team_on_day(
                day_to_swap_with
            )
        )

        days_and_roles_for_original_volunteer[
            original_day
        ] = volunteer_to_swap_with_role_and_group
        days_and_roles_for_swap_volunteer[
            day_to_swap_with
        ] = original_volunteer_role_and_group

        self[original_volunteer] = days_and_roles_for_original_volunteer
        self[volunteer_to_swap_with] = days_and_roles_for_swap_volunteer

        self.list_of_volunteers_with_id_in_role_at_event.swap_roles_and_groups_for_volunteers_in_allocation(
            original_day=original_day,
            day_to_swap_with=day_to_swap_with,
            volunteer_id_to_swap_with=volunteer_to_swap_with.id,
            original_volunteer_id=original_volunteer.id,
        )

    def update_role_and_group_at_event_for_volunteer_on_day(
        self,
        volunteer: Volunteer,
        day: Day,
        new_role: RoleWithSkills,
        new_group: Group = arg_not_passed,  ### if not passed, no change
    ):
        roles_for_volunteer = self.days_and_roles_for_volunteer(volunteer)
        roles_for_volunteer.update_role_and_group_on_day(
            day=day, new_role=new_role, new_group=new_group
        )
        self[volunteer] = roles_for_volunteer

        group_id = arg_not_passed if new_group is arg_not_passed else new_group.id
        role_id = new_role.id
        role_requires_group = new_role.associate_sailing_group

        self.list_of_volunteers_with_id_in_role_at_event.update_role_and_group_for_volunteer_on_day(
            volunteer=volunteer,
            day=day,
            role_id=role_id,
            group_id=group_id,
            role_requires_group=role_requires_group,
        )

    def update_role_and_group_at_event_for_volunteer_on_all_days_when_available(
        self,
        volunteer: Volunteer,
        new_role_and_group: RoleAndGroupAndTeam,
        list_of_days_available: List[Day],
    ):
        roles_for_volunteer = self.days_and_roles_for_volunteer(volunteer)
        roles_for_volunteer.update_role_and_group_at_event_for_volunteer_on_all_days_when_available(
            new_role_and_group=new_role_and_group,
            list_of_days_available=list_of_days_available,
        )
        self[volunteer] = roles_for_volunteer

        role_requires_group = new_role_and_group.role.associate_sailing_group

        self.list_of_volunteers_with_id_in_role_at_event.update_role_and_group_at_event_for_volunteer_on_all_days_when_available(
            role_id=new_role_and_group.role.id,
            volunteer=volunteer,
            group_id=new_role_and_group.group.id,
            list_of_days_available=list_of_days_available,
            role_requires_group=role_requires_group,
        )

    def copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        self,
        volunteer: Volunteer,
        day: Day,
        available_days: DaySelector,
        allow_replacement: bool,
    ):
        roles_for_volunteer = self.days_and_roles_for_volunteer(volunteer)
        roles_for_volunteer.copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
            day=day,
            allow_replacement=allow_replacement,
            list_of_all_days=available_days.days_available(),
        )
        self[volunteer] = roles_for_volunteer

        self.list_of_volunteers_with_id_in_role_at_event.copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
            volunteer_id=volunteer.id,
            day=day,
            allow_replacement=allow_replacement,
            list_of_all_days=available_days.days_available(),
        )

    def drop_volunteer(self, volunteer: Volunteer):
        try:
            existing = self.days_and_roles_for_volunteer(volunteer)
            self.pop(volunteer)
            self._list_of_volunteers_with_id_in_role_at_event = (
                self._list_of_volunteers_with_id_in_role_at_event.drop_volunteer(
                    volunteer
                )
            )
            return [" - removed allocations %s" % str(existing)]
        except:
            return []

    def delete_role_for_volunteer_on_day(self, day: Day, volunteer: Volunteer):
        roles_for_volunteer = self.days_and_roles_for_volunteer(volunteer)
        roles_for_volunteer.delete_role_on_day(day)
        self[volunteer] = roles_for_volunteer

        self.list_of_volunteers_with_id_in_role_at_event.delete_volunteer_in_role_at_event_on_day(
            volunteer=volunteer, day=day
        )

    def count_of_volunteers_in_role_on_day(self, role: RoleWithSkills, day: Day) -> int:
        all_dicts_of_roles_and_groups = self.all_dicts_of_roles_and_groups

        sum_values = [
            1
            for dict_of_roles_for_volunteer in all_dicts_of_roles_and_groups
            if dict_of_roles_for_volunteer.role_and_group_on_day(day).role == role
        ]

        return sum(sum_values)

    def roles_for_team(self, team: Team) -> ListOfRolesWithSkills:
        return self.dict_of_teams_with_roles.roles_for_team(team)

    @property
    def all_groups_at_event(self) -> ListOfGroups:
        all_groups = [
            list(dict_of_roles_and_group.list_of_groups())
            for dict_of_roles_and_group in self.all_dicts_of_roles_and_groups
        ]
        all_groups = flatten(all_groups)
        return ListOfGroups(list(set(all_groups)))

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

        return ListOfRolesWithSkills.from_list_of_roles_with_skills(
            unique_list_of_roles
        )

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

    @property
    def dict_of_teams_with_roles(self) -> DictOfTeamsWithRoles:
        return self._dict_of_teams_and_roles

    @property
    def list_of_groups(self) -> ListOfGroups:
        return self._list_of_groups

    @property
    def list_of_roles_with_skills(self):
        return self._list_of_roles_with_skills


def compose_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups(
    event_id: str,
    list_of_events: ListOfEvents,
    list_of_volunteers: ListOfVolunteers,
    list_of_groups: ListOfGroups,
    list_of_roles_with_skills: ListOfRolesWithSkills,
    dict_of_teams_and_roles: DictOfTeamsWithRoles,
    list_of_volunteers_with_id_in_role_at_event: ListOfVolunteersWithIdInRoleAtEvent,
) -> DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups:
    event = list_of_events.event_with_id(event_id)
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
        dict_of_teams_and_roles=dict_of_teams_and_roles,
        list_of_groups=list_of_groups,
        list_of_volunteers_with_id_in_role_at_event=list_of_volunteers_with_id_in_role_at_event,
        list_of_roles_with_skills=list_of_roles_with_skills,
    )


def compose_raw_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups(
    list_of_volunteers: ListOfVolunteers,
    list_of_groups: ListOfGroups,
    list_of_roles_with_skills: ListOfRolesWithSkills,
    list_of_volunteers_with_id_in_role_at_event: ListOfVolunteersWithIdInRoleAtEvent,
    dict_of_teams_and_roles: DictOfTeamsWithRoles,
) -> Dict[Volunteer, DictOfDaysRolesAndGroupsAndTeams]:
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

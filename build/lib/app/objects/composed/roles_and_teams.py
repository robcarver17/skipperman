from dataclasses import dataclass
from typing import Dict, List

from app.objects.roles_and_teams import Team, ListOfTeams, no_team, RoleLocation
from app.objects.roles_and_teams import ListOfTeamsAndRolesWithIds, TeamsAndRolesWithIds
from app.objects.composed.volunteer_roles import ListOfRolesWithSkills, RoleWithSkills
from app.objects.utils import in_x_not_in_y


@dataclass
class TeamAndIndex:
    team: Team
    index: int

    def location_for_cadet_warning(self) -> RoleLocation:
        return self.team.location_for_cadet_warning


class ListOfTeamsAndIndices(List[TeamAndIndex]):
    @property
    def list_of_teams(self):
        return [team_and_index.team for team_and_index in self]

    def contains_team(self, team: Team):
        if team == no_team:
            return len(self) == 0

        return team in self.list_of_teams


class DictOfTeamsWithRoles(Dict[Team, ListOfRolesWithSkills]):
    def __init__(
        self,
        list_of_teams_and_roles_with_ids: ListOfTeamsAndRolesWithIds,
        list_of_teams: ListOfTeams,
        list_of_roles_with_skills: ListOfRolesWithSkills,
    ):
        super().__init__(
            compose_raw_dict_of_teams_with_roles(
                list_of_teams_and_roles_with_ids=list_of_teams_and_roles_with_ids,
                list_of_teams=list_of_teams,
                list_of_roles_with_skills=list_of_roles_with_skills,
            )
        )
        self._list_of_teams_and_roles_with_ids = list_of_teams_and_roles_with_ids
        self._list_of_roles_with_skills = list_of_roles_with_skills

    def roles_for_team(self, team: Team) -> ListOfRolesWithSkills:
        roles_for_team = self.get(team, ListOfRolesWithSkills())

        return roles_for_team

    def list_of_teams_and_index_given_role(
        self, role: RoleWithSkills
    ) -> ListOfTeamsAndIndices:
        list_of_teams = [
            team
            for team, list_of_roles_with_skills in self.items()
            if role in list_of_roles_with_skills
        ]
        list_of_teams_and_index = [
            TeamAndIndex(team, self[team].index(role)) for team in list_of_teams
        ]
        return ListOfTeamsAndIndices(list_of_teams_and_index)

    def reorder_roles_for_team_given_list_of_names(
        self, team: Team, new_order_of_role_names: List[str]
    ):
        reorder_roles_for_team_given_list_of_names(
            dict_of_teams_with_roles=self,
            team=team,
            new_order_of_role_names=new_order_of_role_names,
        )

    def add_new_named_role_to_team(self, team: Team, new_role_name: str):
        add_new_named_role_to_team(
            dict_of_teams_with_roles=self, team=team, new_role_name=new_role_name
        )

    def refresh_roles_for_team(
        self, team: Team, new_list_of_roles: ListOfRolesWithSkills
    ):
        self._refresh_roles_for_team_to_teams_and_roles_with_ids(
            team=team, new_list_of_roles=new_list_of_roles
        )
        self[team] = new_list_of_roles

    def _refresh_roles_for_team_to_teams_and_roles_with_ids(
        self, team: Team, new_list_of_roles: ListOfRolesWithSkills
    ):
        print(self.list_of_teams_and_roles_with_ids)
        self._remove_roles_for_team_to_teams_and_roles_with_ids(team=team)
        print(self.list_of_teams_and_roles_with_ids)
        self._add_roles_for_team_to_teams_and_roles_with_ids(
            team=team, new_list_of_roles=new_list_of_roles
        )

    def _remove_roles_for_team_to_teams_and_roles_with_ids(self, team: Team):
        list_of_teams_and_roles_with_ids = self.list_of_teams_and_roles_with_ids
        self.list_of_teams_and_roles_with_ids = (
            list_of_teams_and_roles_with_ids.remove_roles_for_team_id(team.id)
        )

    def _add_roles_for_team_to_teams_and_roles_with_ids(
        self, team: Team, new_list_of_roles: ListOfRolesWithSkills
    ):
        list_of_teams_and_roles_with_ids = self.list_of_teams_and_roles_with_ids
        order_idx = 0
        for new_role_with_skill in new_list_of_roles:
            list_of_teams_and_roles_with_ids.append(
                TeamsAndRolesWithIds(
                    team_id=team.id, role_id=new_role_with_skill.id, order_idx=order_idx
                )
            )
            order_idx += 1
        self.list_of_teams_and_roles_with_ids = list_of_teams_and_roles_with_ids

    @property
    def list_of_teams_and_roles_with_ids(self) -> ListOfTeamsAndRolesWithIds:
        return self._list_of_teams_and_roles_with_ids

    @list_of_teams_and_roles_with_ids.setter
    def list_of_teams_and_roles_with_ids(
        self, list_of_teams_and_roles_with_ids: ListOfTeamsAndRolesWithIds
    ):
        self._list_of_teams_and_roles_with_ids = list_of_teams_and_roles_with_ids

    @property
    def list_of_roles_with_skills(self) -> ListOfRolesWithSkills:
        return self._list_of_roles_with_skills


def compose_dict_of_teams_with_roles(
    list_of_teams_and_roles_with_ids: ListOfTeamsAndRolesWithIds,
    list_of_teams: ListOfTeams,
    list_of_roles_with_skills: ListOfRolesWithSkills,
) -> DictOfTeamsWithRoles:
    return DictOfTeamsWithRoles(
        list_of_teams_and_roles_with_ids=list_of_teams_and_roles_with_ids,
        list_of_teams=list_of_teams,
        list_of_roles_with_skills=list_of_roles_with_skills,
    )


def compose_raw_dict_of_teams_with_roles(
    list_of_teams_and_roles_with_ids: ListOfTeamsAndRolesWithIds,
    list_of_teams: ListOfTeams,
    list_of_roles_with_skills: ListOfRolesWithSkills,
) -> Dict[Team, ListOfRolesWithSkills]:
    raw_dict = {}
    for team in list_of_teams:
        list_of_role_ids = list_of_teams_and_roles_with_ids.ordered_role_ids_for_team_id(
            team_id=team.id
        )
        try:
            list_of_roles = list_of_roles_with_skills.subset_for_ids(list_of_role_ids)
        except Exception as e:
            raise Exception(
                "Missing role ID from list of teams and role ids %s" % str(e)
            )

        raw_dict[team] = ListOfRolesWithSkills.from_list_of_roles_with_skills(
            list_of_roles
        )

    return raw_dict


def list_of_all_roles_not_already_in_team(
    dict_of_teams_and_roles: DictOfTeamsWithRoles, team: Team
):
    list_of_roles_in_team = dict_of_teams_and_roles[team]

    return in_x_not_in_y(
        dict_of_teams_and_roles.list_of_roles_with_skills, list_of_roles_in_team
    )


def reorder_roles_for_team_given_list_of_names(
    dict_of_teams_with_roles: DictOfTeamsWithRoles,
    team: Team,
    new_order_of_role_names: List[str],
):
    roles_for_team = dict_of_teams_with_roles[team]
    starting_role_names = roles_for_team.list_of_names()
    list_of_indices = [
        starting_role_names.index(role_name) for role_name in new_order_of_role_names
    ]
    raw_new_list_of_roles = [roles_for_team[idx] for idx in list_of_indices]

    new_list_of_roles = ListOfRolesWithSkills.from_list_of_roles_with_skills(
        raw_new_list_of_roles
    )

    dict_of_teams_with_roles.refresh_roles_for_team(
        team=team, new_list_of_roles=new_list_of_roles
    )


def add_new_named_role_to_team(
    dict_of_teams_with_roles: DictOfTeamsWithRoles, team: Team, new_role_name: str
):
    all_roles = dict_of_teams_with_roles.list_of_roles_with_skills
    list_of_names_in_all_roles = all_roles.list_of_names()
    new_role_idx = list_of_names_in_all_roles.index(new_role_name)
    new_role = all_roles[new_role_idx]
    current_roles_for_team = dict_of_teams_with_roles[team]
    current_roles_for_team.append(new_role)

    dict_of_teams_with_roles.refresh_roles_for_team(
        team=team, new_list_of_roles=current_roles_for_team
    )

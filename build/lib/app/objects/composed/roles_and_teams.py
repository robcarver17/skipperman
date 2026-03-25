from dataclasses import dataclass
from typing import Dict, List

from app.objects.utilities.exceptions import missing_data, MissingData
from app.objects.roles_and_teams import Team, ListOfTeams, no_team, RoleLocation
from app.objects.composed.volunteer_roles import (
    RoleWithSkills,
    ListOfRolesWithSkills,
)
from app.objects.utilities.utils import in_x_not_in_y


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

    def in_instructor_team(self):
        return any(
            [team_and_index.team.is_instructor_team() for team_and_index in self]
        )


class DictOfTeamsWithRoles(Dict[Team, ListOfRolesWithSkills]):
    @property
    def list_of_teams(self) -> ListOfTeams:
        return ListOfTeams(list(self.keys()))

    def roles_in_instructor_team(self) -> ListOfRolesWithSkills:
        instructor_team = self.list_of_teams.instructor_team_from_list()
        return self.roles_for_team(instructor_team)

    def roles_for_team(self, team: Team) -> ListOfRolesWithSkills:
        roles_for_team = self.get(team, missing_data)
        if roles_for_team is missing_data:
            raise MissingData("No roles found for team %s" % team)

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


def list_of_all_roles_not_already_in_team(
    list_of_roles_with_skills: ListOfRolesWithSkills,
    dict_of_teams_and_roles: DictOfTeamsWithRoles,
    team: Team,
):
    list_of_roles_in_team = dict_of_teams_and_roles[team]

    return in_x_not_in_y(list_of_roles_with_skills, list_of_roles_in_team)

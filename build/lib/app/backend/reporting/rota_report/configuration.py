from dataclasses import dataclass

from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)
from app.data_access.configuration.groups import lake_training_group_names
from app.data_access.configuration.skills_and_roles import dict_of_volunteer_teams
from app.objects.day_selectors import DaySelector

TEAM_NAME = "Team name"
ROLE = "Role"
VOLUNTEER = "Volunteer"
GROUP = "Group"
BOAT = "Boat"
DEFAULT_SORT_TEAM = "Default"
SORT_BY_DICT = {
    "Default": [ROLE],
    "Instructors": [ROLE, GROUP],
    "Lake safety": [ROLE, BOAT],
    "Lake helpers": [ROLE, GROUP],
    "River safety": [ROLE, BOAT],
}
TEAMS_WITH_DUPLICATE_LEADERS = ["River safety", "Lake safety"]


def list_of_teams() -> list:
    return list(dict_of_volunteer_teams.keys())


def roles_in_team(team_name: str) -> list:
    return dict_of_volunteer_teams[team_name]


def team_leader_role_for_team(team: str) -> str:
    return dict_of_volunteer_teams.get(team)[0]


specific_parameters_for_volunteer_report = SpecificParametersForTypeOfReport(
    #    entry_columns=[ROLE, VOLUNTEER, GROUP, BOAT],
    group_by_column=TEAM_NAME,
    passed_group_order=dict_of_volunteer_teams,
    report_type="Volunteer rota report",
)


@dataclass
class AdditionalParametersForVolunteerReport:
    days_to_show: DaySelector
    power_boats_only: bool = False

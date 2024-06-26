from dataclasses import dataclass

from app.backend.reporting.options_and_parameters.report_type_specific_parameters import \
    SpecificParametersForTypeOfReport
from app.data_access.configuration.configuration import VOLUNTEER_TEAMS, LAKE_TRAINING_GROUP_NAMES
from app.objects.day_selectors import DaySelector

TEAM_NAME = "Team name"
ROLE = "Role"
VOLUNTEER = "Volunteer"
GROUP = "Group"
BOAT = "Boat"
DEFAULT_SORT_TEAM= 'Default'
SORT_BY_DICT = {
    'Default': [ROLE],
    'Instructors': [ ROLE, GROUP],
    'Lake safety': [ ROLE, BOAT],
    'Lake helpers': [ROLE, GROUP],
    'River safety': [ROLE, BOAT]
}
TEAMS_WITH_DUPLICATE_LEADERS = ['River safety', 'Lake safety']



def list_of_teams() -> list:
    return list(VOLUNTEER_TEAMS.keys())


def roles_in_team(team_name: str) -> list:
    return VOLUNTEER_TEAMS[team_name]


def team_leader_role_for_team(team: str)-> str:
    return VOLUNTEER_TEAMS.get(team)[0]


specific_parameters_for_volunteer_report = SpecificParametersForTypeOfReport(
#    entry_columns=[ROLE, VOLUNTEER, GROUP, BOAT],
    group_by_column=TEAM_NAME,
    passed_group_order=VOLUNTEER_TEAMS,
    report_type="Volunteer rota report"
)


@dataclass
class AdditionalParametersForVolunteerReport:
    days_to_show: DaySelector
    power_boats_only: bool = False

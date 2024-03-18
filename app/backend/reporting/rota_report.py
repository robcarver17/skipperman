from dataclasses import dataclass
from typing import List

import pandas as pd

from app.backend.data.volunteer_rota import load_volunteers_in_role_at_event
from app.backend.data.volunteers import load_all_volunteers
from app.backend.data.resources import load_list_of_patrol_boats, load_list_of_voluteers_at_event_with_patrol_boats
from app.data_access.configuration.configuration import ALL_GROUPS_NAMES, VOLUNTEER_TEAMS
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import CADET_NAME, GROUP_STR_NAME
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)
from app.objects.volunteers import ListOfVolunteers
from app.objects.volunteers_in_roles import ListOfVolunteersInRoleAtEvent, VolunteerInRoleAtEventWithTeamName, \
    VolunteerInRoleAtEvent

specific_parameters_for_volunteer_report = SpecificParametersForTypeOfReport(
    entry_columns=[CADET_NAME],
    group_by_column=GROUP_STR_NAME,
    passed_group_order=ALL_GROUPS_NAMES,
    report_type="Volunteer rota report"
)


@dataclass
class AdditionalParametersForVolunteerReport:
    days_to_show: bool
    include_unallocated_cadets: bool


"""
What is the dataframe

Groups are Role, but we also want to sort by group

For instructors we ideally want a matrix

Need to know who leads are


"""



class GroupOfRolesWithinTeam(List[VolunteerInRoleAtEventWithTeamName]):
    def does_role_require_boat(self):
        requires_boats = [volunteer_in_role_at_event_with_team.volunteer_in_role_at_event.requires_boat for volunteer_in_role_at_event_with_team in self]
        return any(requires_boats)

    def does_role_require_group(self):
        requires_groups = [volunteer_in_role_at_event_with_team.volunteer_in_role_at_event.requires_group for volunteer_in_role_at_event_with_team in self]
        return any(requires_groups)

class Team(List[ GroupOfRolesWithinTeam]):
    pass

    def leader(self) -> pd.DataFrame:
        first_set_of_roles = self[0]
        if len(first_set_of_roles)==0:
            # no leader
            return pd.Series()
        leaders_as_list_of_series


def dataframe_for_team(team: Team, all_volunteers: ListOfVolunteers,):
    pass

def get_df_for_reporting_volunteers_with_flags(
    event: Event
):

    volunteers_in_role_at_event =  load_volunteers_in_role_at_event(event)
    list_of_volunteers_and_roles_by_team = dict()


def get_df_for_reporting_volunteers_for_day(
        event: Event,
        day: Day
):
    volunteers_in_role_at_event = load_volunteers_in_role_at_event(event)
    list_of_volunteers_and_roles_by_team = dict()
    for team_name in list_of_teams():
        volunteers_and_roles_within_team = get_list_of_volunteers_and_roles_within_team_for_day(
            volunteers_in_role_at_event=volunteers_in_role_at_event,
            team_name=team_name, day=day)
        list_of_volunteers_and_roles_by_team[team_name] = volunteers_and_roles_within_team


def get_list_of_volunteers_and_roles_within_team_for_day(day: Day,
                                                 volunteers_in_role_at_event: ListOfVolunteersInRoleAtEvent,
                                                 team_name: str) -> list:
    list_of_volunteers_and_roles_this_team = []
    all_roles_in_team = roles_in_team(team_name)

    for role_name in all_roles_in_team: ## first name will be leader
        list_of_volunteers_doing_roles_this_role = get_list_of_volunteers_doing_specific_role(
                                                                            volunteers_in_role_at_event=volunteers_in_role_at_event,
                                                                            role_name=role_name,
                                                                            team_name=team_name,
                                                                            day=day)
        list_of_volunteers_and_roles_this_team+=list_of_volunteers_doing_roles_this_role

    return Team(list_of_volunteers_and_roles_this_team)


def get_list_of_volunteers_doing_specific_role(day: Day,
                                                 volunteers_in_role_at_event: ListOfVolunteersInRoleAtEvent,
                                                 role_name: str,
                                                    team_name: str) -> GroupOfRolesWithinTeam:

    list_of_volunteers_and_roles_this_role_with_team_name = [
        VolunteerInRoleAtEventWithTeamName(volunteer_in_role_at_event=volunteer_and_role,
            team_name=team_name)
            for volunteer_and_role in volunteers_in_role_at_event
        if volunteer_and_role.role == role_name and volunteer_and_role.day==day]

    return  GroupOfRolesWithinTeam(list_of_volunteers_and_roles_this_role_with_team_name)


def list_of_teams() -> list:
    return list(VOLUNTEER_TEAMS.keys())


def roles_in_team(team_name: str) -> list:
    return VOLUNTEER_TEAMS[team_name]

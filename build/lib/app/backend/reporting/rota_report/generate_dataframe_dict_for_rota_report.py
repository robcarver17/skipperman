from typing import Dict, List

import pandas as pd

from app.backend.reporting.rota_report.components import DataForDfConstruction
from app.backend.reporting.rota_report.configuration import list_of_teams, roles_in_team
from app.backend.reporting.rota_report.teams import Team, dataframe_for_team
from app.objects.day_selectors import DaySelector, Day
from app.objects.events import Event
from app.objects.volunteers_in_roles import ListOfVolunteersInRoleAtEvent, VolunteerInRoleAtEventWithTeamName


def get_df_for_reporting_volunteers_with_flags(
    event: Event,
    days_to_show: DaySelector
) -> Dict[str, pd.DataFrame]:
    data_for_df = DataForDfConstruction.construct_for_event(event)
    list_of_days = days_to_show.days_available()

    dict_of_df = {}
    for day in list_of_days:
        day_name = day.name
        df = get_df_for_reporting_volunteers_for_day(day=day, data_for_df=data_for_df)
        dict_of_df[day_name] = df

    return dict_of_df


def get_df_for_reporting_volunteers_for_day(
        day: Day,
    data_for_df: DataForDfConstruction

) -> pd.DataFrame:
    list_of_team_df = []
    for team_name in list_of_teams():
        team_df = get_df_for_team_on_day(
            team_name=team_name, day=day,
        data_for_df=data_for_df)

        list_of_team_df.append(team_df)

    concat_df = pd.concat(list_of_team_df, axis=0)

    return concat_df


def get_df_for_team_on_day(day: Day,
                           data_for_df: DataForDfConstruction,
                           team_name: str) -> pd.DataFrame:
    team= get_team_on_day(data_for_df=data_for_df, day=day, team_name=team_name)
    df = dataframe_for_team(team=team, data_for_df=data_for_df)

    return df

def get_team_on_day(day: Day,
                           data_for_df: DataForDfConstruction,
                           team_name: str) -> Team:
    list_of_volunteers_and_roles_this_team = []
    all_roles_in_team = roles_in_team(team_name)
    volunteers_in_role_at_event =data_for_df.volunteers_in_role_at_event

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
                                                    team_name: str) -> List[VolunteerInRoleAtEventWithTeamName]:

    list_of_volunteers_and_roles_this_role_with_team_name = [
        VolunteerInRoleAtEventWithTeamName(volunteer_in_role_at_event=volunteer_and_role,
            team_name=team_name)
            for volunteer_and_role in volunteers_in_role_at_event
        if volunteer_and_role.role == role_name and volunteer_and_role.day==day]

    return  list_of_volunteers_and_roles_this_role_with_team_name

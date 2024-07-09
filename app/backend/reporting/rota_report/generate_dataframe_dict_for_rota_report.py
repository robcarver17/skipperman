from typing import Dict, List

import pandas as pd
from app.data_access.storage_layer.api import DataLayer

from app.data_access.configuration.skills_and_roles import RIVER_SAFETY, LAKE_SAFETY
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.reporting.rota_report.components import DataForDfConstruction
from app.backend.reporting.rota_report.configuration import (
    list_of_teams,
    roles_in_team,
    BOAT,
    TEAM_NAME,
    ROLE,
    GROUP,
)
from app.backend.reporting.rota_report.teams import (
    Team,
    dataframe_for_team,
    sort_df_by_power_boat,
)
from app.objects.day_selectors import DaySelector, Day
from app.objects.events import Event
from app.objects.volunteers_in_roles import (
    ListOfVolunteersInRoleAtEvent,
    VolunteerInRoleAtEventWithTeamName,
)


def get_df_for_reporting_volunteers_with_flags(
    event: Event,
    days_to_show: DaySelector,
    interface: abstractInterface,
    power_boats_only: bool = False,
) -> Dict[str, pd.DataFrame]:
    data_for_df = DataForDfConstruction.construct_for_event(
        event=event, data_layer=interface.data
    )
    list_of_days = days_to_show.align_with_list_of_days(event.weekdays_in_event())
    dict_of_df = {}
    for day in list_of_days:
        day_name = day.name
        df_for_reporting_volunteers_for_day = get_df_for_reporting_volunteers_for_day(
            day=day, data_for_df=data_for_df
        )
        if len(df_for_reporting_volunteers_for_day) == 0:
            continue

        df_for_reporting_volunteers_for_day = apply_sorts_and_transforms_to_df(
            df_for_reporting_volunteers_for_day=df_for_reporting_volunteers_for_day,
            data_for_df=data_for_df,
            power_boats_only=power_boats_only,
        )
        dict_of_df[day_name] = df_for_reporting_volunteers_for_day

    return dict_of_df


def get_df_for_reporting_volunteers_for_day(
    day: Day,
    data_for_df: DataForDfConstruction,
) -> pd.DataFrame:
    list_of_team_df = []
    for team_name in list_of_teams():
        team_df = get_df_for_team_on_day(
            team_name=team_name, day=day, data_for_df=data_for_df
        )

        list_of_team_df.append(team_df)

    concat_df = pd.concat(list_of_team_df, axis=0)

    return concat_df


def get_df_for_team_on_day(
    day: Day, data_for_df: DataForDfConstruction, team_name: str
) -> pd.DataFrame:
    team = get_team_on_day(data_for_df=data_for_df, day=day, team_name=team_name)
    df = dataframe_for_team(team=team, data_for_df=data_for_df)

    return df


def get_team_on_day(
    day: Day,
    data_for_df: DataForDfConstruction,
    team_name: str,
) -> Team:
    list_of_volunteers_and_roles_this_team = []
    all_roles_in_team = roles_in_team(team_name)
    volunteers_in_role_at_event = data_for_df.volunteers_in_role_at_event

    for role_name in all_roles_in_team:  ## first name will be leader
        list_of_volunteers_doing_roles_this_role = (
            get_list_of_volunteers_doing_specific_role(
                volunteers_in_role_at_event=volunteers_in_role_at_event,
                role_name=role_name,
                team_name=team_name,
                day=day,
            )
        )
        list_of_volunteers_and_roles_this_team += (
            list_of_volunteers_doing_roles_this_role
        )

    return Team(list_of_volunteers_and_roles_this_team)


def get_list_of_volunteers_doing_specific_role(
    day: Day,
    volunteers_in_role_at_event: ListOfVolunteersInRoleAtEvent,
    role_name: str,
    team_name: str,
) -> List[VolunteerInRoleAtEventWithTeamName]:
    list_of_volunteers_and_roles_this_role_with_team_name = [
        VolunteerInRoleAtEventWithTeamName(
            volunteer_in_role_at_event=volunteer_and_role, team_name=team_name
        )
        for volunteer_and_role in volunteers_in_role_at_event
        if volunteer_and_role.role == role_name and volunteer_and_role.day == day
    ]

    return list_of_volunteers_and_roles_this_role_with_team_name


def apply_sorts_and_transforms_to_df(
    df_for_reporting_volunteers_for_day: pd.DataFrame,
    data_for_df: DataForDfConstruction,
    power_boats_only: bool = True,
):
    if power_boats_only:
        df_for_reporting_volunteers_for_day = transform_df_into_power_boat_only(
            df_for_reporting_volunteers_for_day=df_for_reporting_volunteers_for_day,
            data_for_df=data_for_df,
        )

    df_for_reporting_volunteers_for_day = apply_textual_transforms_to_df(
        df_for_reporting_volunteers_for_day=df_for_reporting_volunteers_for_day
    )

    return df_for_reporting_volunteers_for_day


def transform_df_into_power_boat_only(
    df_for_reporting_volunteers_for_day: pd.DataFrame,
    data_for_df: DataForDfConstruction,
) -> pd.DataFrame:
    new_df = sort_df_by_power_boat(
        df_for_reporting_volunteers_for_day=df_for_reporting_volunteers_for_day,
        data_for_df=data_for_df,
        include_no_power_boat=False,
    )
    pseudo_teams = [
        find_pseudo_power_team_given_row(row) for __, row in new_df.iterrows()
    ]
    print(pseudo_teams)
    new_df[TEAM_NAME] = pseudo_teams

    return new_df


def find_pseudo_power_team_given_row(row: pd.Series) -> str:
    boat = row[BOAT]
    if "lake" in boat.lower():
        return LAKE_SAFETY
    else:
        return RIVER_SAFETY


def apply_textual_transforms_to_df(df_for_reporting_volunteers_for_day: pd.DataFrame):
    df_for_reporting_volunteers_for_day[BOAT] = df_for_reporting_volunteers_for_day[
        BOAT
    ].apply(text_given_boat)
    df_for_reporting_volunteers_for_day[ROLE] = df_for_reporting_volunteers_for_day[
        ROLE
    ].apply(text_given_role)
    df_for_reporting_volunteers_for_day[GROUP] = df_for_reporting_volunteers_for_day[
        GROUP
    ].apply(text_given_group)

    return df_for_reporting_volunteers_for_day


def text_given_role(role: str) -> str:
    if len(role) == 0:
        return ""
    return role + ":"


def text_given_group(group: str) -> str:
    if len(group) == 0:
        return ""
    return "- %s" % group


def text_given_boat(boat: str) -> str:
    if len(boat) == 0:
        return ""
    return "(%s)" % boat

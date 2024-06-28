from typing import List

import pandas as pd
from app.data_access.configuration.configuration import (
    VOLUNTEER_ROLES,
    ALL_GROUPS_NAMES,
)

from app.backend.reporting.rota_report.components import (
    DataForDfConstruction,
    df_row_for_volunteer_in_role_at_event,
)
from app.backend.reporting.rota_report.configuration import (
    DEFAULT_SORT_TEAM,
    SORT_BY_DICT,
    TEAMS_WITH_DUPLICATE_LEADERS,
    team_leader_role_for_team,
    BOAT,
    ROLE,
    GROUP,
)
from app.objects.volunteers_in_roles import VolunteerInRoleAtEventWithTeamName


class Team(List[VolunteerInRoleAtEventWithTeamName]):
    pass


def get_team_name(team: Team) -> str:
    team_name = team[0].team_name
    return team_name


def dataframe_for_team(data_for_df: DataForDfConstruction, team: Team) -> pd.DataFrame:
    if len(team) == 0:
        return pd.DataFrame()

    leaders_df = dataframe_for_team_leaders(data_for_df=data_for_df, team=team)
    others_df = get_sorted_df_for_rest_of_team(data_for_df=data_for_df, team=team)

    combined_df = combine_and_drop_initial_duplicates(
        leaders_df=leaders_df, others_df=others_df
    )
    combined_df.reset_index(inplace=True, drop=True)

    return combined_df


def dataframe_for_team_leaders(data_for_df: DataForDfConstruction, team: Team):
    matching_volunteers = list_of_volunteers_in_leadership_position(team)

    df_for_team_leaders = [
        df_row_for_volunteer_in_role_at_event(
            volunteer_in_role_at_event_with_team_name=volunteer, data_for_df=data_for_df
        )
        for volunteer in matching_volunteers
    ]

    return pd.DataFrame(df_for_team_leaders)


def get_sorted_df_for_rest_of_team(
    data_for_df: DataForDfConstruction, team: Team
) -> pd.DataFrame:
    if does_team_have_duplicate_leader(team):
        volunteers_to_exclude = []
    else:
        volunteers_to_exclude = list_of_volunteers_in_leadership_position(team)

    list_of_rest_of_team = [
        df_row_for_volunteer_in_role_at_event(
            volunteer_in_role_at_event_with_team_name=volunteer, data_for_df=data_for_df
        )
        for volunteer in team
        if not volunteer in volunteers_to_exclude
    ]

    if len(list_of_rest_of_team) == 0:
        return pd.DataFrame()

    as_df = pd.DataFrame(list_of_rest_of_team)
    sort_order_list = get_sort_order_for_team(team)
    for sort_order in sort_order_list:
        if sort_order == ROLE:
            as_df = sort_df_by_role(
                df_for_reporting_volunteers_for_day=as_df, data_for_df=data_for_df
            )
        elif sort_order == GROUP:
            as_df = sort_df_by_group(
                df_for_reporting_volunteers_for_day=as_df, data_for_df=data_for_df
            )
        elif sort_order == BOAT:
            as_df = sort_df_by_power_boat(as_df, data_for_df=data_for_df)

    return as_df


def combine_and_drop_initial_duplicates(
    leaders_df: pd.DataFrame, others_df: pd.DataFrame
) -> pd.DataFrame:
    if len(leaders_df) == 0:
        return others_df
    if len(others_df) == 0:
        return leaders_df

    leaders_df.reset_index(inplace=True, drop=True)
    others_df.reset_index(inplace=True, drop=True)

    duplicates = True
    while duplicates:
        if len(leaders_df) == 0:
            break
        if len(others_df) == 0:
            break
        first_row_of_other = others_df.iloc[0]
        last_row_of_leaders = leaders_df.iloc[-1]

        if rows_match(first_row_of_other, last_row_of_leaders):
            others_df = others_df.drop(others_df.index[0], axis=0)
        else:
            break

    return pd.concat([leaders_df, others_df], axis=0)


def rows_match(some_row: pd.Series, other_row: pd.Series):
    return all(some_row == other_row)


def does_team_have_duplicate_leader(team: Team) -> bool:
    return get_team_name(team) in TEAMS_WITH_DUPLICATE_LEADERS


def get_sort_order_for_team(team: Team) -> List[str]:
    team_name = get_team_name(team)
    order = SORT_BY_DICT.get(team_name, None)
    if order is None:
        return SORT_BY_DICT[DEFAULT_SORT_TEAM]
    else:
        return order


def list_of_volunteers_in_leadership_position(
    team: Team,
) -> List[VolunteerInRoleAtEventWithTeamName]:
    team_name = get_team_name(team)
    lead_role = team_leader_role_for_team(team_name)
    matching_volunteers = [
        volunteer
        for volunteer in team
        if volunteer.volunteer_in_role_at_event.role == lead_role
    ]

    return matching_volunteers


def sort_df_by_power_boat(
    df_for_reporting_volunteers_for_day: pd.DataFrame,
    data_for_df: DataForDfConstruction,
    include_no_power_boat: bool = True,
) -> pd.DataFrame:
    all_boats_in_order = data_for_df.all_patrol_boats
    new_df = pd.DataFrame()
    for boat in all_boats_in_order:
        subset_df = df_for_reporting_volunteers_for_day[
            df_for_reporting_volunteers_for_day[BOAT] == boat.name
        ]
        new_df = pd.concat([new_df, subset_df], axis=0)
        df_for_reporting_volunteers_for_day = df_for_reporting_volunteers_for_day[
            df_for_reporting_volunteers_for_day[BOAT] != boat.name
        ]

    if include_no_power_boat:
        new_df = pd.concat([new_df, df_for_reporting_volunteers_for_day], axis=0)

    return new_df


def sort_df_by_role(
    df_for_reporting_volunteers_for_day: pd.DataFrame,
    data_for_df: DataForDfConstruction,
    include_no_role: bool = True,
) -> pd.DataFrame:
    all_roles_in_order = VOLUNTEER_ROLES
    new_df = pd.DataFrame()
    for role in all_roles_in_order:
        subset_df = df_for_reporting_volunteers_for_day[
            df_for_reporting_volunteers_for_day[ROLE] == role
        ]
        new_df = pd.concat([new_df, subset_df], axis=0)
        df_for_reporting_volunteers_for_day = df_for_reporting_volunteers_for_day[
            df_for_reporting_volunteers_for_day[ROLE] != role
        ]

    if include_no_role:
        new_df = pd.concat([new_df, df_for_reporting_volunteers_for_day], axis=0)

    return new_df


def sort_df_by_group(
    df_for_reporting_volunteers_for_day: pd.DataFrame,
    data_for_df: DataForDfConstruction,
    include_no_group: bool = True,
) -> pd.DataFrame:
    all_groups = ALL_GROUPS_NAMES
    new_df = pd.DataFrame()
    for group in all_groups:
        subset_df = df_for_reporting_volunteers_for_day[
            df_for_reporting_volunteers_for_day[GROUP] == group
        ]
        new_df = pd.concat([new_df, subset_df], axis=0)
        df_for_reporting_volunteers_for_day = df_for_reporting_volunteers_for_day[
            df_for_reporting_volunteers_for_day[GROUP] != group
        ]

    if include_no_group:
        new_df = pd.concat([new_df, df_for_reporting_volunteers_for_day], axis=0)

    return new_df

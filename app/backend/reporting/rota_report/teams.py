from copy import copy
from typing import List, Dict

import pandas as pd

from app.backend.reporting.rota_report.components import (
    df_row_for_volunteer_in_role_at_event,
)
from app.backend.reporting.rota_report.configuration import (
    BOAT,
    ROLE,
    GROUP,
)
from app.objects.composed.volunteer_roles import RoleWithSkills
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    VolunteerWithRoleGroupAndTeamAtEvent,
)
from app.objects.composed.volunteers_with_all_event_data import (
    DictOfAllEventDataForVolunteers,
)
from app.objects.utils import flatten
from app.objects.roles_and_teams import Team


def dataframe_for_team(
    volunteer_event_data: DictOfAllEventDataForVolunteers,
    team: Team,
    dict_of_volunteers_in_team_on_day_at_event: Dict[
        RoleWithSkills, List[VolunteerWithRoleGroupAndTeamAtEvent]
    ],
    include_no_power_boat: bool = True,
) -> pd.DataFrame:
    if len(dict_of_volunteers_in_team_on_day_at_event) == 0:
        return pd.DataFrame()

    ## first entry should be team leaders - these are not sorted
    leadership_role = list(dict_of_volunteers_in_team_on_day_at_event.keys())[0]
    volunteers_in_team_leader_roles = dict_of_volunteers_in_team_on_day_at_event[
        leadership_role
    ]

    dict_of_other_volunteers = copy(dict_of_volunteers_in_team_on_day_at_event)
    dict_of_other_volunteers.pop(leadership_role)

    leaders_df = dataframe_for_team_leaders(
        team=team,
        volunteers_in_team_leader_roles=volunteers_in_team_leader_roles,
        volunteer_event_data=volunteer_event_data,
    )
    others_df = get_sorted_df_for_rest_of_team(
        team=team,
        dict_of_other_volunteers=dict_of_other_volunteers,
        volunteer_event_data=volunteer_event_data,
        include_no_power_boat=include_no_power_boat,
    )

    combined_df = combine_and_drop_initial_duplicates(
        leaders_df=leaders_df, others_df=others_df
    )
    combined_df.reset_index(inplace=True, drop=True)

    return combined_df


def dataframe_for_team_leaders(
    volunteer_event_data: DictOfAllEventDataForVolunteers,
    team: Team,
    volunteers_in_team_leader_roles: List[VolunteerWithRoleGroupAndTeamAtEvent],
):

    df_for_team_leaders = [
        df_row_for_volunteer_in_role_at_event(
            volunteer_event_data=volunteer_event_data,
            team=team,
            volunteer_with_role_and_group_and_team=volunteer_with_role_and_group_and_team,
        )
        for volunteer_with_role_and_group_and_team in volunteers_in_team_leader_roles
    ]

    return pd.DataFrame(df_for_team_leaders)


def get_sorted_df_for_rest_of_team(
    volunteer_event_data: DictOfAllEventDataForVolunteers,
    team: Team,
    dict_of_other_volunteers: Dict[
        RoleWithSkills, List[VolunteerWithRoleGroupAndTeamAtEvent]
    ],
    include_no_power_boat: bool = True,
) -> pd.DataFrame:

    list_of_volunteers = flatten(
        [
            volunteers_for_role
            for volunteers_for_role in list(dict_of_other_volunteers.values())
        ]
    )

    if len(list_of_volunteers) == 0:
        return pd.DataFrame()

    list_of_rest_of_team = [
        df_row_for_volunteer_in_role_at_event(
            volunteer_with_role_and_group_and_team=volunteer_with_role_and_group_and_team,
            volunteer_event_data=volunteer_event_data,
            team=team,
        )
        for volunteer_with_role_and_group_and_team in list_of_volunteers
    ]

    as_df = pd.DataFrame(list_of_rest_of_team)
    if team.is_instructor_team():
        sort_order_list = [ROLE, GROUP]
    else:
        sort_order_list = [ROLE, GROUP, BOAT]

    for sort_order in sort_order_list:
        if sort_order == ROLE:
            as_df = sort_df_by_role(
                df_for_reporting_volunteers_for_day=as_df,
                volunteer_event_data=volunteer_event_data,
            )
        elif sort_order == GROUP:
            as_df = sort_df_by_group(
                df_for_reporting_volunteers_for_day=as_df,
                volunteer_event_data=volunteer_event_data,
            )
        elif sort_order == BOAT:
            as_df = sort_df_by_power_boat(
                as_df,
                volunteer_event_data=volunteer_event_data,
                include_no_power_boat=include_no_power_boat,
            )

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


def sort_df_by_power_boat(
    df_for_reporting_volunteers_for_day: pd.DataFrame,
    volunteer_event_data: DictOfAllEventDataForVolunteers,
    include_no_power_boat: bool = True,
) -> pd.DataFrame:
    all_boats_in_order = (
        volunteer_event_data.dict_of_volunteers_at_event_with_patrol_boats.list_of_unique_boats_at_event_including_unallocated()
    ) ## FIXME PERHAPS REMOVE UNALLOCATED?
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
    volunteer_event_data: DictOfAllEventDataForVolunteers,
    include_no_role: bool = True,
) -> pd.DataFrame:
    all_roles_in_order = (
        volunteer_event_data.dict_of_volunteers_at_event_with_days_and_roles.list_of_roles_with_skills
    )
    new_df = pd.DataFrame()
    for role in all_roles_in_order:
        subset_df = df_for_reporting_volunteers_for_day[
            df_for_reporting_volunteers_for_day[ROLE] == role.name
        ]
        new_df = pd.concat([new_df, subset_df], axis=0)
        df_for_reporting_volunteers_for_day = df_for_reporting_volunteers_for_day[
            df_for_reporting_volunteers_for_day[ROLE] != role.name
        ]

    if include_no_role:
        new_df = pd.concat([new_df, df_for_reporting_volunteers_for_day], axis=0)

    return new_df


def sort_df_by_group(
    df_for_reporting_volunteers_for_day: pd.DataFrame,
    volunteer_event_data: DictOfAllEventDataForVolunteers,
    include_no_group: bool = True,
) -> pd.DataFrame:

    all_groups = (
        volunteer_event_data.dict_of_volunteers_at_event_with_days_and_roles.list_of_groups
    )
    new_df = pd.DataFrame()
    for group in all_groups:
        subset_df = df_for_reporting_volunteers_for_day[
            df_for_reporting_volunteers_for_day[GROUP] == group.name
        ]
        new_df = pd.concat([new_df, subset_df], axis=0)
        df_for_reporting_volunteers_for_day = df_for_reporting_volunteers_for_day[
            df_for_reporting_volunteers_for_day[GROUP] != group.name
        ]

    if include_no_group:
        new_df = pd.concat([new_df, df_for_reporting_volunteers_for_day], axis=0)

    return new_df

from typing import Dict, List

import pandas as pd

from app.data_access.store.object_store import ObjectStore

from app.backend.reporting.rota_report.configuration import (
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
from app.backend.volunteers.volunteers_at_event import (
    get_dict_of_all_event_data_for_volunteers,
)
from app.objects.composed.volunteer_roles import RoleWithSkills
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    VolunteerWithRoleGroupAndTeamAtEvent,
)
from app.objects.composed.volunteers_with_all_event_data import (
    DictOfAllEventDataForVolunteers,
)

from app.objects.day_selectors import DaySelector, Day
from app.objects.events import Event

RIVER_SAFETY = "River safety"
LAKE_SAFETY = "Lake safety"


def get_df_for_reporting_volunteers_with_flags(
    object_store: ObjectStore,
    event: Event,
    days_to_show: DaySelector,
    power_boats_only: bool = False,
) -> Dict[str, pd.DataFrame]:
    volunteer_event_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )

    list_of_days = days_to_show.align_with_list_of_days(
        event.days_in_event()
    ).days_available()

    dict_of_df = dict(
        [
            (
                day.name,
                get_and_transform_df_for_reporting_volunteers_for_day(
                    volunteer_event_data=volunteer_event_data,
                    day=day,
                    power_boats_only=power_boats_only,
                ),
            )
            for day in list_of_days
        ]
    )

    dict_of_df_excluding_empty = dict(
        [(day_name, df) for day_name, df in dict_of_df.items() if len(df) > 0]
    )

    print("days in dict %s" % str(dict_of_df_excluding_empty.keys()))

    return dict_of_df_excluding_empty


def get_and_transform_df_for_reporting_volunteers_for_day(
    day: Day,
    volunteer_event_data: DictOfAllEventDataForVolunteers,
    power_boats_only: bool,
) -> pd.DataFrame:
    df_for_reporting_volunteers_for_day = get_df_for_reporting_volunteers_for_day(
        day=day, volunteer_event_data=volunteer_event_data
    )
    if len(df_for_reporting_volunteers_for_day) == 0:
        return pd.DataFrame()

    df_for_reporting_volunteers_for_day = apply_sorts_and_transforms_to_df(
        df_for_reporting_volunteers_for_day=df_for_reporting_volunteers_for_day,
        volunteer_event_data=volunteer_event_data,
        power_boats_only=power_boats_only,
    )

    return df_for_reporting_volunteers_for_day


def get_df_for_reporting_volunteers_for_day(
    day: Day, volunteer_event_data: DictOfAllEventDataForVolunteers
) -> pd.DataFrame:
    list_of_teams = (
        volunteer_event_data.dict_of_volunteers_at_event_with_days_and_roles.all_teams_at_event
    )
    if len(list_of_teams)==0:
        return pd.DataFrame()
    list_of_team_df = []
    for team in list_of_teams:
        team_df = get_df_for_team_on_day(
            volunteer_event_data=volunteer_event_data,
            team=team,
            day=day,
        )

        list_of_team_df.append(team_df)

    concat_df = pd.concat(list_of_team_df, axis=0)

    return concat_df


def get_df_for_team_on_day(
    volunteer_event_data: DictOfAllEventDataForVolunteers, team: Team, day: Day
) -> pd.DataFrame:
    dict_of_volunteers_in_team_on_day_at_event = (
        get_dict_of_volunteers_in_team_on_day_at_event(
            volunteer_event_data=volunteer_event_data, team=team, day=day
        )
    )
    df = dataframe_for_team(
        dict_of_volunteers_in_team_on_day_at_event=dict_of_volunteers_in_team_on_day_at_event,
        volunteer_event_data=volunteer_event_data,
        team=team,
    )

    return df


def get_dict_of_volunteers_in_team_on_day_at_event(
    day: Day,
    volunteer_event_data: DictOfAllEventDataForVolunteers,
    team: Team,
) -> Dict[RoleWithSkills, List[VolunteerWithRoleGroupAndTeamAtEvent]]:

    dict_of_volunteers_and_roles_this_team = {}
    all_roles_in_team = volunteer_event_data.dict_of_volunteers_at_event_with_days_and_roles.roles_for_team(
        team
    )

    for role in all_roles_in_team:  ## first name will be leader
        list_of_volunteers_doing_roles_this_role = volunteer_event_data.dict_of_volunteers_at_event_with_days_and_roles.list_of_volunteers_with_roles_and_groups_and_teams_doing_role_on_day(
            day=day, role=role
        )
        dict_of_volunteers_and_roles_this_team[role] = (
            list_of_volunteers_doing_roles_this_role
        )

    return dict_of_volunteers_and_roles_this_team


def apply_sorts_and_transforms_to_df(
    df_for_reporting_volunteers_for_day: pd.DataFrame,
    volunteer_event_data: DictOfAllEventDataForVolunteers,
    power_boats_only: bool = True,
):
    if power_boats_only:
        df_for_reporting_volunteers_for_day = transform_df_into_power_boat_only(
            df_for_reporting_volunteers_for_day=df_for_reporting_volunteers_for_day,
            volunteer_event_data=volunteer_event_data,
        )

    df_for_reporting_volunteers_for_day = apply_textual_transforms_to_df(
        df_for_reporting_volunteers_for_day=df_for_reporting_volunteers_for_day
    )

    return df_for_reporting_volunteers_for_day


def transform_df_into_power_boat_only(
    df_for_reporting_volunteers_for_day: pd.DataFrame,
    volunteer_event_data: DictOfAllEventDataForVolunteers,
) -> pd.DataFrame:

    new_df = sort_df_by_power_boat(
        df_for_reporting_volunteers_for_day=df_for_reporting_volunteers_for_day,
        volunteer_event_data=volunteer_event_data,
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

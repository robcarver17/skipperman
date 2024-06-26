from dataclasses import dataclass
from typing import List, Dict

import pandas as pd
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.volunteer_rota import VolunteerRotaData
from app.backend.volunteers.volunteer_rota import (
    DEPRECATE_get_volunteers_in_role_at_event_with_active_allocations,
)
from app.data_access.configuration.configuration import (
    ALL_GROUPS_NAMES,
    VOLUNTEER_ROLES,
)
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import GROUP_UNALLOCATED_TEXT, Group
from app.objects.volunteers_in_roles import (
    ListOfVolunteersInRoleAtEvent,
    NO_ROLE_SET,
    RoleAndGroup,
    TeamAndGroup,
    get_list_of_volunteer_teams,
    ListOfTargetForRoleAtEvent,
)
from app.objects.abstract_objects.abstract_tables import PandasDFTable


@dataclass
class RowInTableWithActualAndTargetsForRole:
    role: str
    daily_counts: Dict[Day, int]
    target: int
    worst_shortfall: int


def get_list_of_actual_and_targets_for_roles_at_event(
    interface: abstractInterface, event: Event
) -> List[RowInTableWithActualAndTargetsForRole]:
    volunteers_in_roles_at_event = (
        DEPRECATE_get_volunteers_in_role_at_event_with_active_allocations(
            event=event, interface=interface
        )
    )
    targets_at_event = get_volunteer_targets_at_event(interface=interface, event=event)

    all_rows = [
        get_row_in_table_with_actual_and_targets_for_roles_at_event(
            event=event,
            role=role,
            volunteers_in_roles_at_event=volunteers_in_roles_at_event,
            targets_at_event=targets_at_event,
        )
        for role in VOLUNTEER_ROLES
    ]

    return all_rows


def get_volunteer_targets_at_event(
    interface: abstractInterface, event: Event
) -> ListOfTargetForRoleAtEvent:
    volunteer_data = VolunteerRotaData(interface.data)
    return volunteer_data.get_list_of_targets_for_role_at_event(event)


def get_row_in_table_with_actual_and_targets_for_roles_at_event(
    event: Event,
    role: str,
    volunteers_in_roles_at_event: ListOfVolunteersInRoleAtEvent,
    targets_at_event: ListOfTargetForRoleAtEvent,
) -> RowInTableWithActualAndTargetsForRole:
    daily_counts = {}
    for day in event.weekdays_in_event():
        volunteer_count = [
            1
            for volunteer in volunteers_in_roles_at_event
            if volunteer.role == role and volunteer.day == day
        ]
        total_count = sum(volunteer_count)
        daily_counts[day] = total_count

    min_count = min(daily_counts.values())
    target = targets_at_event.get_target_for_role(role=role)
    worst_shortfall = target - min_count

    return RowInTableWithActualAndTargetsForRole(
        role=role,
        daily_counts=daily_counts,
        target=target,
        worst_shortfall=worst_shortfall,
    )


def save_new_volunteer_target(
    interface: abstractInterface, event: Event, role: str, target: int
):
    volunteer_data = VolunteerRotaData(interface.data)
    volunteer_data.save_new_volunteer_target(event=event, role=role, target=target)


####


def get_summary_list_of_roles_and_groups_for_events(
    interface: abstractInterface, event: Event
) -> PandasDFTable:
    return PandasDFTable(
        get_summary_list_of_roles_and_groups_for_events_as_pd_df(
            interface=interface, event=event
        )
    )


def get_summary_list_of_roles_and_groups_for_events_as_pd_df(
    interface: abstractInterface, event: Event
) -> pd.DataFrame:
    all_day_summaries = list_of_day_summaries_for_roles_at_event(
        interface=interface, event=event
    )
    single_df = from_list_of_day_summaries_to_single_df(
        all_day_summaries=all_day_summaries, event=event
    )

    return single_df


def list_of_day_summaries_for_roles_at_event(
    interface: abstractInterface, event: Event
) -> List[pd.DataFrame]:
    volunteers_in_roles_at_event = (
        DEPRECATE_get_volunteers_in_role_at_event_with_active_allocations(
            event=event, interface=interface
        )
    )
    days_at_event = event.weekdays_in_event()
    all_day_summaries = []
    for day in days_at_event:
        this_day_summary = get_summary_of_roles_and_groups_for_events_on_day(
            day=day, volunteers_in_roles_at_event=volunteers_in_roles_at_event
        )
        all_day_summaries.append(this_day_summary)

    return all_day_summaries


def get_summary_of_roles_and_groups_for_events_on_day(
    day: Day, volunteers_in_roles_at_event: ListOfVolunteersInRoleAtEvent
) -> pd.DataFrame:
    list_of_roles_and_groups = (
        volunteers_in_roles_at_event.list_of_roles_and_groups_at_event_for_day(day)
    )
    all_roles = VOLUNTEER_ROLES + [
        NO_ROLE_SET
    ]  ## ordered, doesn't include unallocated do those last
    all_group_names = [
        GROUP_UNALLOCATED_TEXT
    ] + ALL_GROUPS_NAMES  ## ordered, doesn't include unallocated we put these first

    summary_dict = {}
    for group_name in all_group_names:
        for role in all_roles:
            role_and_group = RoleAndGroup(role=role, group=Group(group_name))
            count = role_and_group_with_count(
                role_and_group, list_of_roles_and_groups=list_of_roles_and_groups
            )
            summary_dict[role_and_group] = [count]

    return pd.DataFrame(summary_dict).transpose()


def role_and_group_with_count(
    role_and_group: RoleAndGroup, list_of_roles_and_groups: List[RoleAndGroup]
) -> int:
    matching = [
        role_and_group_in_list
        for role_and_group_in_list in list_of_roles_and_groups
        if role_and_group_in_list == role_and_group
    ]

    return len(matching)


## TEAMS


def get_summary_list_of_teams_and_groups_for_events(
    interface: abstractInterface, event: Event
) -> PandasDFTable:
    return PandasDFTable(
        get_summary_list_of_teams_and_groups_for_events_as_pd_df(
            interface=interface, event=event
        )
    )


def get_summary_list_of_teams_and_groups_for_events_as_pd_df(
    interface: abstractInterface, event: Event
) -> pd.DataFrame:
    all_day_summaries = list_of_day_summaries_teams_and_groups_at_event(
        interface=interface, event=event
    )
    single_df = from_list_of_day_summaries_to_single_df(
        all_day_summaries=all_day_summaries, event=event
    )

    return single_df


def list_of_day_summaries_teams_and_groups_at_event(
    interface: abstractInterface, event: Event
) -> List[pd.DataFrame]:
    volunteers_in_roles_at_event = (
        DEPRECATE_get_volunteers_in_role_at_event_with_active_allocations(
            event=event, interface=interface
        )
    )
    days_at_event = event.weekdays_in_event()
    all_day_summaries = []
    for day in days_at_event:
        this_day_summary = get_summary_of_teams_and_groups_for_events_on_day(
            day=day, volunteers_in_roles_at_event=volunteers_in_roles_at_event
        )
        all_day_summaries.append(this_day_summary)

    return all_day_summaries


def get_summary_of_teams_and_groups_for_events_on_day(
    day: Day, volunteers_in_roles_at_event: ListOfVolunteersInRoleAtEvent
) -> pd.DataFrame:
    list_of_teams_and_groups = (
        volunteers_in_roles_at_event.list_of_first_teams_and_groups_at_event_for_day(
            day
        )
    )
    all_teams = get_list_of_volunteer_teams() + [
        NO_ROLE_SET
    ]  ## ordered, doesn't include unallocated do those last
    all_group_names = [
        GROUP_UNALLOCATED_TEXT
    ] + ALL_GROUPS_NAMES  ## ordered, doesn't include unallocated we put these first

    summary_dict = {}
    for group_name in all_group_names:
        for team in all_teams:
            team_and_group = TeamAndGroup(team=team, group=Group(group_name))
            count = team_and_group_with_count(
                team_and_group, list_of_teams_and_groups=list_of_teams_and_groups
            )
            summary_dict[team_and_group] = [count]

    return pd.DataFrame(summary_dict).transpose()


def team_and_group_with_count(
    team_and_group: TeamAndGroup, list_of_teams_and_groups: List[RoleAndGroup]
) -> int:
    matching = [
        team_and_group_in_list
        for team_and_group_in_list in list_of_teams_and_groups
        if team_and_group_in_list == team_and_group
    ]

    return len(matching)


# SHARED


def from_list_of_day_summaries_to_single_df(
    all_day_summaries: List[pd.DataFrame], event: Event
) -> pd.DataFrame:
    days_at_event = event.weekdays_in_event()
    single_df = pd.concat(all_day_summaries, axis=1)
    single_df = single_df.loc[~(single_df == 0).all(axis=1)]  ## missing values
    single_df.columns = [day.name for day in days_at_event]

    return single_df

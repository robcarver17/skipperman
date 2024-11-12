from typing import List

import pandas as pd
from app.backend.groups.list_of_groups import get_list_of_groups

from app.backend.volunteers.roles_and_teams import get_list_of_teams

from app.OLD_backend.rota.volunteer_rota import (
    get_volunteers_in_role_at_event_with_active_allocations,
)

from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache

from app.data_access.store.object_store import ObjectStore

from app.backend.volunteers.volunteers_at_event import (
    get_dict_of_all_event_data_for_volunteers,
)
from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    RoleAndGroupAndTeam,
)
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import unallocated_group, ListOfGroups
from app.objects.roles_and_teams import no_team, ListOfTeams
from app.objects.volunteer_roles_and_groups_with_id import (
    TeamAndGroup,
    ListOfVolunteersWithIdInRoleAtEvent,
    NO_ROLE_SET,
    RoleAndGroupDEPRECATE,
)
from build.lib.app.data_access.configuration.skills_and_roles import (
    all_volunteer_role_names,
)


def get_summary_list_of_roles_and_groups_for_events(
    cache: AdHocCache, event: Event
) -> PandasDFTable:
    return PandasDFTable(
        get_summary_list_of_roles_and_groups_for_events_as_pd_df(
            cache=cache, event=event
        )
    )


def get_summary_list_of_roles_and_groups_for_events_as_pd_df(
    cache: AdHocCache, event: Event
) -> pd.DataFrame:
    all_day_summaries = get_list_of_day_summaries_for_roles_at_event(
        cache=cache, event=event
    )
    single_df = from_list_of_day_summaries_to_single_df(
        all_day_summaries=all_day_summaries, event=event
    )

    return single_df


def get_list_of_day_summaries_for_roles_at_event(
    cache: AdHocCache, event: Event
) -> List[pd.DataFrame]:
    volunteers_in_roles_at_event = cache.get_from_cache(
        get_volunteers_in_role_at_event_with_active_allocations, event=event
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
    day: Day, volunteers_in_roles_at_event: ListOfVolunteersWithIdInRoleAtEvent
) -> pd.DataFrame:
    list_of_roles_and_groups = (
        volunteers_in_roles_at_event.list_of_roles_and_groups_at_event_for_day(day)
    )
    list_of_all_role_names = all_volunteer_role_names + [
        NO_ROLE_SET
    ]  ## ordered, doesn't include unallocated do those last
    raise Exception("")
    # list_of_all_group_names = [
    #    GROUP_UNALLOCATED_TEXT
    # ] + all_groups_names  ## ordered, doesn't include unallocated we put these first

    summary_dict = {}
    for group_name in list_of_all_group_names:
        for role in list_of_all_role_names:
            role_and_group = RoleAndGroupDEPRECATE(role=role, group=Group(group_name))
            count = role_and_group_with_count(
                role_and_group, list_of_roles_and_groups=list_of_roles_and_groups
            )
            summary_dict[role_and_group] = [count]

    return pd.DataFrame(summary_dict).transpose()


def role_and_group_with_count(
    role_and_group: RoleAndGroupDEPRECATE,
    list_of_roles_and_groups: List[RoleAndGroupDEPRECATE],
) -> int:
    matching = [
        role_and_group_in_list
        for role_and_group_in_list in list_of_roles_and_groups
        if role_and_group_in_list == role_and_group
    ]

    return len(matching)


def get_summary_list_of_teams_and_groups_for_events(
    object_store: ObjectStore, event: Event
) -> PandasDFTable:
    return PandasDFTable(
        get_summary_list_of_teams_and_groups_for_events_as_pd_df(
            object_store=object_store, event=event
        )
    )


def get_summary_list_of_teams_and_groups_for_events_as_pd_df(
    object_store: ObjectStore, event: Event
) -> pd.DataFrame:
    all_day_summaries = get_list_of_day_summaries_teams_and_groups_at_event(
        object_store=object_store, event=event
    )
    single_df = from_list_of_day_summaries_to_single_df(
        all_day_summaries=all_day_summaries, event=event
    )

    return single_df


def get_list_of_day_summaries_teams_and_groups_at_event(
    object_store: ObjectStore, event: Event
) -> List[pd.DataFrame]:
    volunteer_event_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    if len(volunteer_event_data)==0:
        return []
    volunteers_in_roles_at_event = (
        volunteer_event_data.dict_of_volunteers_at_event_with_days_and_role
    )

    list_of_teams = get_list_of_teams(object_store)
    all_teams_at_event = ListOfTeams(volunteers_in_roles_at_event.all_teams_at_event)
    sorted_teams_at_event = all_teams_at_event.sort_to_match_other_team_list_order(
        list_of_teams
    )

    all_groups = get_list_of_groups(object_store)
    all_groups_at_event = ListOfGroups(
        volunteers_in_roles_at_event.all_groups_at_event + [unallocated_group]
    )
    sorted_groups_at_event = all_groups_at_event.sort_to_match_other_group_list_order(
        all_groups
    )

    days_at_event = event.weekdays_in_event()
    all_day_summaries = []
    for day in days_at_event:
        this_day_summary = get_summary_of_teams_and_groups_for_events_on_day(
            day=day,
            volunteers_in_roles_at_event=volunteers_in_roles_at_event,
            sorted_teams_at_event=sorted_teams_at_event,
            sorted_groups_at_event=sorted_groups_at_event,
        )
        all_day_summaries.append(this_day_summary)

    return all_day_summaries


def get_summary_of_teams_and_groups_for_events_on_day(
    day: Day,
    volunteers_in_roles_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    sorted_teams_at_event: ListOfTeams,
    sorted_groups_at_event: ListOfGroups,
) -> pd.DataFrame:
    list_of_roles_and_groups_at_event_on_day = (
        volunteers_in_roles_at_event.list_of_all_roles_and_groups_and_teams_for_day(day)
    )
    summary_dict = {}
    for team in sorted_teams_at_event:
        for group in sorted_groups_at_event:
            team_and_group = TeamAndGroup(team=team, group=group)
            count = team_and_group_with_count(
                team_and_group,
                list_of_roles_and_groups_at_event_on_day=list_of_roles_and_groups_at_event_on_day,
            )
            summary_dict[team_and_group] = [count]

    return pd.DataFrame(summary_dict).transpose()


def team_and_group_with_count(
    team_and_group: TeamAndGroup,
    list_of_roles_and_groups_at_event_on_day: List[RoleAndGroupAndTeam],
) -> int:
    matching = [
        team_and_group_in_list
        for team_and_group_in_list in list_of_roles_and_groups_at_event_on_day
        if team_and_group_in_list.matches_team_and_group(
            team=team_and_group.team, group=team_and_group.group
        )
    ]

    return len(matching)


def from_list_of_day_summaries_to_single_df(
    all_day_summaries: List[pd.DataFrame], event: Event
) -> pd.DataFrame:
    if len(all_day_summaries)==0:
        return pd.DataFrame()
    days_at_event = event.weekdays_in_event()
    single_df = pd.concat(all_day_summaries, axis=1)
    single_df = single_df.loc[~(single_df == 0).all(axis=1)]  ## missing values
    single_df.columns = [day.name for day in days_at_event]

    return single_df

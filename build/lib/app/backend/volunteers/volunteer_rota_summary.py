from typing import List

import pandas as pd

from app.backend.data.volunteer_rota import get_volunteers_in_role_at_event
from app.data_access.configuration.configuration import VOLUNTEER_ROLES, ALL_GROUPS_NAMES
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import GROUP_UNALLOCATED_TEXT, Group
from app.objects.volunteers_in_roles import ListOfVolunteersInRoleAtEvent, NO_ROLE_SET, RoleAndGroup
from app.objects.abstract_objects.abstract_tables import PandasDFTable

def get_summary_list_of_roles_and_groups_for_events(event: Event) -> PandasDFTable:
    return PandasDFTable(get_summary_list_of_roles_and_groups_for_events_as_pd_df(event))


def get_summary_list_of_roles_and_groups_for_events_as_pd_df(event: Event) -> pd.DataFrame:
    volunteers_in_roles_at_event = get_volunteers_in_role_at_event(event)
    days_at_event = event.weekdays_in_event()
    all_day_summaries = []
    for day in days_at_event:
        this_day_summary = get_summary_of_roles_and_groups_for_events_on_day(
            day=day,
            volunteers_in_roles_at_event=volunteers_in_roles_at_event
        )
        all_day_summaries.append(this_day_summary)

    single_df= pd.concat(all_day_summaries, axis=1)

    single_df = single_df.loc[~(single_df==0).all(axis=1)] ## missing values
    single_df.columns = [day.name for day in days_at_event]

    return single_df


def get_summary_of_roles_and_groups_for_events_on_day(
                                                      day: Day,
                                                      volunteers_in_roles_at_event: ListOfVolunteersInRoleAtEvent) -> pd.DataFrame:

    list_of_roles_and_groups = volunteers_in_roles_at_event.list_of_roles_and_groups_at_event_for_day(day)
    all_roles = VOLUNTEER_ROLES+[NO_ROLE_SET] ## ordered, doesn't include unallocated do those last
    all_group_names = [GROUP_UNALLOCATED_TEXT]+ALL_GROUPS_NAMES ## ordered, doesn't include unallocated we put these first

    summary_dict = {}
    for role in all_roles:
        for group_name in all_group_names:
            role_and_group = RoleAndGroup(role=role, group=Group(group_name))
            count = role_and_group_with_count(role_and_group,
                                                              list_of_roles_and_groups=list_of_roles_and_groups)
            summary_dict[role_and_group] = [count]


    return pd.DataFrame(summary_dict).transpose()



def role_and_group_with_count(role_and_group: RoleAndGroup, list_of_roles_and_groups: List[RoleAndGroup]) -> int:
    matching = [role_and_group_in_list for role_and_group_in_list in list_of_roles_and_groups if
                role_and_group_in_list == role_and_group]

    return len(matching)

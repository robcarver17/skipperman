from typing import Dict, List

import pandas as pd

from app.backend.group_allocations.cadet_event_allocations import get_unallocated_cadets, load_allocation_for_event
from app.backend.data.cadets_at_event import load_cadets_at_event
from app.objects.day_selectors import DaySelector, Day
from app.objects.groups import ListOfCadetIdsWithGroups
from app.objects.events import Event
from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.groups import Group, GROUP_UNALLOCATED, ALL_GROUPS_NAMES

def summarise_allocations_for_event(event: Event) -> PandasDFTable:
    list_of_cadet_ids_with_groups = load_allocation_for_event(event)

    cadets_at_event = load_cadets_at_event(event)
    availability_dict = dict([(cadet.id, cadet.availability)
                              for cadet in cadets_at_event.list_of_active_cadets_at_event()])

    groups = get_sorted_groups_plus_unalloacted(list_of_cadet_ids_with_groups)
    rows = [get_row_for_group(group=group,
                              event=event,
                              list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
                              availability_dict=availability_dict) for group in groups]

    df = pd.concat(rows, axis=1)
    df.columns = groups

    return PandasDFTable(df.transpose())

def get_sorted_groups_plus_unalloacted(list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups) ->List[Group]:
    groups_in_passed_list = list(set(list_of_cadet_ids_with_groups.groups))
    group_names_in_passed_list = [group.group_name for group in groups_in_passed_list]
    group_names = [group_name for group_name in ALL_GROUPS_NAMES if group_name in group_names_in_passed_list] ## preserve order
    groups = [Group(group_name) for group_name in group_names]

    return groups+[GROUP_UNALLOCATED]

def get_row_for_group(group:Group, event: Event,
                      list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups,
                        availability_dict: Dict[str, DaySelector]
                      ) -> pd.DataFrame:

    list_of_cadet_ids_for_group = get_relevant_cadet_ids_for_group(group=group,
                                                                   list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
                                                                   event=event)

    counts= [get_count_on_day_for_group(list_of_cadet_ids_for_group=list_of_cadet_ids_for_group,
                                        availability_dict=availability_dict,
                                        day=day) for day in event.weekdays_in_event()]

    day_names = [day.name for day in event.weekdays_in_event()]

    return pd.DataFrame(counts, index=day_names)


def get_relevant_cadet_ids_for_group(group: Group,
                                     event: Event,
                                     list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups)-> List[str]:
    if group == GROUP_UNALLOCATED:
        unallocated_cadets = get_unallocated_cadets(
            event=event,
            list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
        )
        list_of_ids = unallocated_cadets.list_of_ids
    else:
        list_of_ids = [cadet_and_group.cadet_id for cadet_and_group in list_of_cadet_ids_with_groups if cadet_and_group.group == group]

    return list_of_ids

def get_count_on_day_for_group(list_of_cadet_ids_for_group: list,
                               availability_dict: Dict[str, DaySelector],
                               day: Day) -> int:

    present = [1 for cadet_id in list_of_cadet_ids_for_group if availability_dict[cadet_id].available_on_day(day)]

    return sum(present)



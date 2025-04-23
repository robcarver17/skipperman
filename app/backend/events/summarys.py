from typing import Dict, List, Callable

import pandas as pd
from app.objects.cadets import ListOfCadets

from app.objects.composed.cadets_at_event_with_groups import (
    DictOfCadetsWithDaysAndGroupsAtEvent,
)

from app.data_access.store.object_store import ObjectStore

from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_dict_of_all_event_info_for_cadets,
    get_attendance_matrix_for_list_of_cadets_at_event,
)
from app.objects.day_selectors import Day, DaySelector
from app.objects.events import Event
from app.objects.exceptions import arg_not_passed
from app.objects.groups import Group


def summarise_allocations_for_event(
    object_store: ObjectStore, event: Event
) -> pd.DataFrame:
    cadets_at_event_data = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event, active_only=True
    )

    availability_dict = get_attendance_matrix_for_list_of_cadets_at_event(
        object_store=object_store, event=event
    )
    dict_of_cadets_with_days_and_groups = (
        cadets_at_event_data.dict_of_cadets_with_days_and_groups
    )

    groups = dict_of_cadets_with_days_and_groups.all_groups_at_event()
    groups.remove_unallocated()

    return summarise_generic_counts_for_event_over_days_returning_df(
        get_id_function=get_relevant_cadets_for_group_on_day,
        event=event,
        groups=groups,
        availability_dict=availability_dict,
        list_of_ids_with_groups=dict_of_cadets_with_days_and_groups,
    )


def get_relevant_cadets_for_group_on_day(
    group: Group,
    event: Event,
    list_of_ids_with_groups: DictOfCadetsWithDaysAndGroupsAtEvent,
) -> Dict[Day, ListOfCadets]:
    result_dict = {}
    for day in event.days_in_event():
        result_dict[day] = list_of_ids_with_groups.list_of_cadets_in_group_on_day(
            day=day, group=group
        )

    return result_dict



def summarise_generic_counts_for_event_over_days_returning_df(
    event: Event,
    list_of_ids_with_groups: list,
    availability_dict: dict,
    groups: list,
    get_id_function: Callable,
    group_labels: list = arg_not_passed,
) -> pd.DataFrame:
    rows = [
        get_row_for_group(
            group=group,
            event=event,
            get_id_function=get_id_function,
            list_of_ids_with_groups=list_of_ids_with_groups,
            availability_dict=availability_dict,
        )
        for group in groups
    ]

    if len(rows) == 0:
        return PandasDFTable(pd.DataFrame())

    df = pd.concat(rows, axis=1)
    if group_labels is arg_not_passed:
        group_labels = groups

    df.columns = group_labels

    df = df.transpose()

    return df



def get_row_for_group(
    group,
    event: Event,
    list_of_ids_with_groups: list,
    availability_dict: Dict[str, DaySelector],
    get_id_function: Callable,
) -> pd.DataFrame:
    dict_of_ids_for_group_by_day = get_id_function(
        group=group, list_of_ids_with_groups=list_of_ids_with_groups, event=event
    )

    counts = [
        get_count_on_day_for_group(
            dict_of_ids_for_group_by_day=dict_of_ids_for_group_by_day,
            availability_dict=availability_dict,
            day=day,
        )
        for day in event.days_in_event()
    ]

    day_names = [day.name for day in event.days_in_event()]

    return pd.DataFrame(counts, index=day_names)


def get_count_on_day_for_group(
    dict_of_ids_for_group_by_day: Dict[Day, List[str]],
    availability_dict: Dict[str, DaySelector],
    day: Day,
) -> int:
    present = [
        available_on_day(id, availability_dict=availability_dict, day=day)
        for id in dict_of_ids_for_group_by_day[day]
    ]

    return sum(present)


def available_on_day(
    id: str, availability_dict: Dict[str, DaySelector], day: Day
) -> int:
    availability_for_id = availability_dict.get(id, None)
    if availability_for_id is None:
        return 0
    if availability_for_id.available_on_day(day):
        return 1
    else:
        return 0

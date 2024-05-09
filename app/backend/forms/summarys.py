from typing import Callable, Dict, List

import pandas as pd

from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.constants import arg_not_passed
from app.objects.day_selectors import DaySelector, Day
from app.objects.events import Event


def DEPRECATE_summarise_generic_counts_for_event(event: Event,
                                                 list_of_ids_with_groups: list,
                                                 availability_dict: dict,
                                                 groups: list,
                                                 get_id_function: Callable,
                                                 group_labels: list = arg_not_passed
                                                 ) -> PandasDFTable:

    rows = [DEPRECATE_get_row_for_group(group=group,
                                        event=event,
                                        get_id_function=get_id_function,
                                        list_of_ids_with_groups=list_of_ids_with_groups,
                                        availability_dict=availability_dict) for group in groups]

    if len(rows)==0:
        return PandasDFTable(pd.DataFrame())

    df = pd.concat(rows, axis=1)
    if group_labels is arg_not_passed:
        group_labels = groups

    df.columns = group_labels


    return PandasDFTable(df.transpose())


def DEPRECATE_get_row_for_group(group, event: Event,
                                list_of_ids_with_groups: list,
                                availability_dict: Dict[str, DaySelector],
                                get_id_function: Callable
                                ) -> pd.DataFrame:

    list_of_ids_for_group = get_id_function(group=group,
                                                   list_of_ids_with_groups=list_of_ids_with_groups,
                                                   event=event)

    counts= [DEPRECATE_get_count_on_day_for_group(list_of_ids_for_group=list_of_ids_for_group,
                                                  availability_dict=availability_dict,
                                                  day=day) for day in event.weekdays_in_event()]

    day_names = [day.name for day in event.weekdays_in_event()]

    return pd.DataFrame(counts, index=day_names)


def DEPRECATE_get_count_on_day_for_group(list_of_ids_for_group: list,
                                         availability_dict: Dict[str, DaySelector],
                                         day: Day) -> int:

    present = [available_on_day(id, availability_dict=availability_dict, day=day) for id in list_of_ids_for_group]

    return sum(present)

def available_on_day(id: str, availability_dict: Dict[str, DaySelector],
                     day: Day) -> int:
    availability_for_id = availability_dict.get(id, None)
    if availability_for_id is None:
        return 0
    if availability_for_id.available_on_day(day):
        return 1
    else:
        return 0


def summarise_generic_counts_for_event_over_days(event: Event,
                                                 list_of_ids_with_groups: list,
                                                 availability_dict: dict,
                                                 groups: list,
                                                 get_id_function: Callable,
                                                 group_labels: list = arg_not_passed
                                                 ) -> PandasDFTable:

    rows = [get_row_for_group(group=group,
                                        event=event,
                                        get_id_function=get_id_function,
                                        list_of_ids_with_groups=list_of_ids_with_groups,
                                        availability_dict=availability_dict) for group in groups]

    if len(rows)==0:
        return PandasDFTable(pd.DataFrame())

    df = pd.concat(rows, axis=1)
    if group_labels is arg_not_passed:
        group_labels = groups

    df.columns = group_labels


    return PandasDFTable(df.transpose())


def get_row_for_group(group, event: Event,
                                list_of_ids_with_groups: list,
                                availability_dict: Dict[str, DaySelector],
                                get_id_function: Callable
                                ) -> pd.DataFrame:

    dict_of_ids_for_group_by_day = get_id_function(group=group,
                                                   list_of_ids_with_groups=list_of_ids_with_groups,
                                                   event=event)

    counts= [get_count_on_day_for_group(dict_of_ids_for_group_by_day=dict_of_ids_for_group_by_day,
                                                  availability_dict=availability_dict,
                                                  day=day) for day in event.weekdays_in_event()]

    day_names = [day.name for day in event.weekdays_in_event()]

    return pd.DataFrame(counts, index=day_names)


def get_count_on_day_for_group(dict_of_ids_for_group_by_day:  Dict[Day, List[str]],
                                         availability_dict: Dict[str, DaySelector],
                                         day: Day) -> int:

    present = [available_on_day(id, availability_dict=availability_dict, day=day) for id in dict_of_ids_for_group_by_day[day]]

    return sum(present)

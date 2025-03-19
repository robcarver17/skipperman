import os
from typing import Dict

import pandas as pd

from app.backend.qualifications_and_ticks.progress import get_expected_qualifications_for_list_of_cadets_as_df
from app.data_access.init_directories import download_directory
from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.backend.cadets.list_of_cadets import get_list_of_cadets
from app.backend.groups.previous_groups import get_dict_of_group_allocations_for_all_events_active_cadets_only
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.composed.cadets_at_event_with_groups import DictOfCadetsWithDaysAndGroupsAtEvent
from app.objects.events import Event, ListOfEvents


def write_group_history_and_qualification_status_to_temp_csv_file_and_return_filename(
    interface: abstractInterface
) -> str:
    list_of_cadets = get_list_of_cadets(object_store=interface.object_store)
    df_of_qualifications = get_expected_qualifications_for_list_of_cadets_as_df(
        object_store=interface.object_store, list_of_cadets=list_of_cadets
    )

    filename = temp_file_name()
    df_of_qualifications.to_csv(filename, index=False)

    return filename


def temp_file_name() -> str:
    return os.path.join(download_directory, "temp_file.csv")

def get_df_of_history_for_active_cadets(object_store: ObjectStore, list_of_cadets: ListOfCadets):
    dict_of_group_allocations = get_dict_of_group_allocations_for_all_events_active_cadets_only(
        object_store=object_store
    )

    list_of_events = ListOfEvents(list(dict_of_group_allocations.keys()))

    list_of_dict_of_names = [
        get_dict_of_group_name_for_cadet_across_events(dict_of_group_allocations=dict_of_group_allocations,
                                                       cadet=cadet,
                                                       list_of_events=list_of_events) for cadet in list_of_cadets
    ]

    return pd.DataFrame(list_of_dict_of_names)

def get_dict_of_group_name_for_cadet_across_events(dict_of_group_allocations: Dict[Event, DictOfCadetsWithDaysAndGroupsAtEvent],
                                      cadet: Cadet, list_of_events: ListOfEvents) -> Dict[str, str]:

    dict_of_names = dict([(event.name, get_group_name_for_cadet_at_event(dict_of_group_allocations=dict_of_group_allocations,
                                                       cadet=cadet,
                                                       event=event)) for event in list_of_events])

    return dict_of_names

def get_group_name_for_cadet_at_event(dict_of_group_allocations: Dict[Event,DictOfCadetsWithDaysAndGroupsAtEvent], cadet: Cadet, event: Event) -> str:
    allocations_at_event = dict_of_group_allocations[event]
    group = allocations_at_event.get_most_common_group_for_cadet(cadet)

    return group.name


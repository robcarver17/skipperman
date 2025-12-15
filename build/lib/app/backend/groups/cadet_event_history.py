import os
from typing import Dict

import pandas as pd

from app.backend.qualifications_and_ticks.progress import (
    get_expected_qualifications_for_list_of_cadets_as_df,
)
from app.data_access.init_directories import download_directory
from app.data_access.store.object_store import ObjectStore
from app.backend.cadets.list_of_cadets import DEPRECATE_get_list_of_cadets
from app.backend.groups.previous_groups import (
    get_dict_of_group_allocations_for_all_events_active_cadets_only,
)
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.composed.cadets_at_event_with_groups import (
    DictOfCadetsWithDaysAndGroupsAtEvent,
)
from app.objects.events import Event, ListOfEvents
from app.objects.utilities.exceptions import missing_data


def write_group_history_and_qualification_status_to_temp_csv_file_and_return_filename(
    object_store: ObjectStore,
) -> str:
    list_of_cadets = DEPRECATE_get_list_of_cadets(object_store=object_store)
    list_of_cadets = list_of_cadets.current_members_only()

    df_of_qualifications = get_expected_qualifications_for_list_of_cadets_as_df(
        object_store=object_store, list_of_cadets=list_of_cadets
    )
    df_of_history = get_df_of_history_for_active_cadets(
        object_store=object_store, list_of_cadets=list_of_cadets
    )

    both_df = pd.concat([df_of_qualifications, df_of_history], axis=1)
    both_df.insert(
        0,
        "Date of Birth",
        pd.Series(
            [cadet.date_of_birth for cadet in list_of_cadets], index=both_df.index
        ),
    )

    filename = temp_file_name()
    both_df.to_csv(filename, index=True)

    return filename


def temp_file_name() -> str:
    return os.path.join(download_directory, "temp_file.csv")


def get_df_of_history_for_active_cadets(
    object_store: ObjectStore, list_of_cadets: ListOfCadets
):
    dict_of_group_allocations = (
        get_dict_of_group_allocations_for_all_events_active_cadets_only(
            object_store=object_store
        )
    )

    list_of_events = ListOfEvents(list(dict_of_group_allocations.keys()))

    list_of_dict_of_names = [
        get_dict_of_group_name_for_cadet_across_events(
            dict_of_group_allocations=dict_of_group_allocations,
            cadet=cadet,
            list_of_events=list_of_events,
        )
        for cadet in list_of_cadets
    ]

    df = pd.DataFrame(list_of_dict_of_names)
    df.index = list_of_cadets.list_of_names()

    return df


def get_dict_of_group_name_for_cadet_across_events(
    dict_of_group_allocations: Dict[Event, DictOfCadetsWithDaysAndGroupsAtEvent],
    cadet: Cadet,
    list_of_events: ListOfEvents,
) -> Dict[str, str]:
    dict_of_names = dict(
        [
            (
                str(event),
                get_group_name_for_cadet_at_event(
                    dict_of_group_allocations=dict_of_group_allocations,
                    cadet=cadet,
                    event=event,
                ),
            )
            for event in list_of_events
        ]
    )

    return dict_of_names


def get_group_name_for_cadet_at_event(
    dict_of_group_allocations: Dict[Event, DictOfCadetsWithDaysAndGroupsAtEvent],
    cadet: Cadet,
    event: Event,
) -> str:
    allocations_at_event = dict_of_group_allocations[event]
    group = allocations_at_event.get_most_common_group_for_cadet(
        cadet, default_group=missing_data
    )
    if group is missing_data:
        return "Not at event"

    return group.name

import datetime

import pandas as pd

from app.backend.cadets.list_of_cadets import get_list_of_cadets
from app.backend.events.list_of_events import get_list_of_events
from app.backend.groups.cadet_event_history import (
    get_df_of_history_for_active_cadets,
    temp_file_name,
)
from app.backend.groups.previous_groups import (
    get_dict_of_event_allocations_for_single_cadet_given_list_of_events,
)
from app.backend.qualifications_and_ticks.progress import (
    get_expected_qualifications_for_list_of_cadets_as_df,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.events import ListOfEvents
from app.objects.utilities.exceptions import arg_not_passed


def write_new_sailors_recent_group_history_and_qualification_status_to_temp_csv_file_and_return_filename(
    object_store: ObjectStore, date_cutoff: datetime.date = arg_not_passed
) -> str:
    if date_cutoff is arg_not_passed:
        date_cutoff = datetime.date.today() - datetime.timedelta(days=366)

    list_of_cadets = get_list_of_cadets_whose_first_event_was_after_date(
        object_store=object_store, date_cutoff=date_cutoff
    )

    list_of_recent_events = get_list_of_events_after_cuttoff(
        object_store=object_store, date_cutoff=date_cutoff
    )

    df_of_history = get_df_of_history_for_active_cadets(
        object_store=object_store,
        list_of_cadets=list_of_cadets,
        list_of_events=list_of_recent_events,
    )

    df_of_qualifications = get_expected_qualifications_for_list_of_cadets_as_df(
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


def get_list_of_cadets_whose_first_event_was_after_date(
    object_store: ObjectStore, date_cutoff: datetime.date
):
    list_of_cadets = get_list_of_cadets(object_store)
    list_of_events = get_list_of_events(object_store)

    return ListOfCadets(
        [
            cadet
            for cadet in list_of_cadets
            if was_cadet_first_event_after_date(
                object_store=object_store,
                list_of_events=list_of_events,
                cadet=cadet,
                date_cutoff=date_cutoff,
            )
        ]
    )


def was_cadet_first_event_after_date(
    object_store: ObjectStore,
    cadet: Cadet,
    date_cutoff: datetime.date,
    list_of_events: ListOfEvents,
):
    allocations = get_dict_of_event_allocations_for_single_cadet_given_list_of_events(
        object_store=object_store, cadet=cadet, list_of_events=list_of_events
    )
    if len(allocations) == 0:
        return False

    events_attended = ListOfEvents(list(allocations.keys()))
    earliest_event = events_attended.sort_by_start_date_asc()[0]

    return earliest_event.start_date > date_cutoff


def get_list_of_events_after_cuttoff(
    object_store: ObjectStore, date_cutoff: datetime.date
):
    list_of_events = get_list_of_events(object_store)
    return ListOfEvents(
        [event for event in list_of_events if event.start_date > date_cutoff]
    )

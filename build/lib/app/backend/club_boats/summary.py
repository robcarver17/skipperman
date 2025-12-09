from typing import Dict, List

import pandas as pd

from app.backend.volunteers.volunteers_at_event import (
    get_attendance_matrix_for_list_of_volunteers_at_event,
)
from app.objects.cadets import Cadet

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_attendance_matrix_for_list_of_cadets_at_event,
)

from app.data_access.store.object_store import ObjectStore

from app.backend.events.summarys import (
    summarise_generic_counts_for_event_over_days_returning_df,
)
from app.objects.club_dinghies import ClubDinghy
from app.objects.day_selectors import Day
from app.objects.events import Event

from app.objects.composed.people_at_event_with_club_dinghies import (
    DictOfPeopleAndClubDinghiesAtEvent,
)
from app.backend.club_boats.cadets_with_club_dinghies_at_event import (
    get_dict_of_people_and_club_dinghies_at_event,
)
from app.objects.volunteers import Volunteer


def summarise_club_boat_allocations_for_event(
    object_store: ObjectStore, event: Event
) -> pd.DataFrame:
    df_cadets = summarise_club_boat_allocations_for_cadets_at_event(
        object_store=object_store,
        event=event,
    )
    df_volunteers = summarise_club_boat_allocations_for_volunteers_at_event(
        object_store=object_store, event=event
    )

    return df_cadets + df_volunteers


def summarise_club_boat_allocations_for_cadets_at_event(
    object_store: ObjectStore, event: Event
) -> pd.DataFrame:
    dict_of_cadets_and_club_dinghies_at_event = (
        get_dict_of_people_and_club_dinghies_at_event(
            object_store=object_store, event=event
        )
    )
    list_of_dinghys_at_event = (
        dict_of_cadets_and_club_dinghies_at_event.unique_sorted_list_of_allocated_club_dinghys_allocated_at_event()
    )

    row_names = list_of_dinghys_at_event.list_of_names()
    availability_dict = get_attendance_matrix_for_list_of_cadets_at_event(
        object_store=object_store, event=event
    )

    df = summarise_generic_counts_for_event_over_days_returning_df(
        get_id_function=get_relevant_cadets_for_club_dinghy,
        event=event,
        groups=list_of_dinghys_at_event,
        group_labels=row_names,
        availability_dict=availability_dict,
        list_of_ids_with_groups=dict_of_cadets_and_club_dinghies_at_event,  ## ignore typing error
    )

    return df


def get_relevant_cadets_for_club_dinghy(
    group: ClubDinghy,
    event: Event,
    list_of_ids_with_groups: DictOfPeopleAndClubDinghiesAtEvent,
) -> Dict[Day, List[Cadet]]:
    ## map from generic to specific var names. Event is not used
    dinghy = group
    dict_of_cadets_with_club_dinghies_at_event = list_of_ids_with_groups

    result_dict = {}
    for day in event.days_in_event():
        result_dict[day] = [
            cadet
            for cadet in dict_of_cadets_with_club_dinghies_at_event.list_of_cadets
            if dict_of_cadets_with_club_dinghies_at_event.club_dinghys_for_person(
                cadet
            ).has_specific_dinghy_on_day(day=day, dinghy=dinghy)
        ]

    return result_dict


def summarise_club_boat_allocations_for_volunteers_at_event(
    object_store: ObjectStore, event: Event
) -> pd.DataFrame:
    dict_of_cadets_and_club_dinghies_at_event = (
        get_dict_of_people_and_club_dinghies_at_event(
            object_store=object_store, event=event
        )
    )
    list_of_dinghys_at_event = (
        dict_of_cadets_and_club_dinghies_at_event.unique_sorted_list_of_allocated_club_dinghys_allocated_at_event()
    )

    row_names = list_of_dinghys_at_event.list_of_names()
    availability_dict = get_attendance_matrix_for_list_of_volunteers_at_event(
        object_store=object_store, event=event
    )

    df = summarise_generic_counts_for_event_over_days_returning_df(
        get_id_function=get_relevant_volunteers_for_club_dinghy,
        event=event,
        groups=list_of_dinghys_at_event,
        group_labels=row_names,
        availability_dict=availability_dict,
        list_of_ids_with_groups=dict_of_cadets_and_club_dinghies_at_event,  ## ignore typing error
    )

    return df


def get_relevant_volunteers_for_club_dinghy(
    group: ClubDinghy,
    event: Event,
    list_of_ids_with_groups: DictOfPeopleAndClubDinghiesAtEvent,
) -> Dict[Day, List[Volunteer]]:
    ## map from generic to specific var names. Event is not used
    dinghy = group
    dict_of_volunteers_with_club_dinghies_at_event = list_of_ids_with_groups

    result_dict = {}
    for day in event.days_in_event():
        result_dict[day] = [
            volunteer
            for volunteer in dict_of_volunteers_with_club_dinghies_at_event.list_of_volunteers
            if dict_of_volunteers_with_club_dinghies_at_event.club_dinghys_for_person(
                volunteer
            ).has_specific_dinghy_on_day(day=day, dinghy=dinghy)
        ]

    return result_dict

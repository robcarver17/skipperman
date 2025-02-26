from typing import Dict, List

from app.objects.cadets import Cadet

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_attendance_matrix_for_list_of_cadets_at_event,
)

from app.data_access.store.object_store import ObjectStore

from app.backend.events.summarys import summarise_generic_counts_for_event_over_days
from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.club_dinghies import ClubDinghy
from app.objects.day_selectors import Day
from app.objects.events import Event

from app.objects.composed.cadets_at_event_with_club_dinghies import (
    DictOfCadetsAndClubDinghiesAtEvent,
)
from app.backend.club_boats.cadets_with_club_dinghies_at_event import (
    get_dict_of_cadets_and_club_dinghies_at_event,
)


def summarise_club_boat_allocations_for_event(
    object_store: ObjectStore, event: Event
) -> PandasDFTable:
    dict_of_cadets_and_club_dinghies_at_event = (
        get_dict_of_cadets_and_club_dinghies_at_event(
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

    table = summarise_generic_counts_for_event_over_days(
        get_id_function=get_relevant_cadets_for_club_dinghy,
        event=event,
        groups=list_of_dinghys_at_event,
        group_labels=row_names,
        availability_dict=availability_dict,
        list_of_ids_with_groups=dict_of_cadets_and_club_dinghies_at_event,  ## ignore typing error
    )

    return table


def get_relevant_cadets_for_club_dinghy(
    group: ClubDinghy,
    event: Event,
    list_of_ids_with_groups: DictOfCadetsAndClubDinghiesAtEvent,
) -> Dict[Day, List[Cadet]]:
    ## map from generic to specific var names. Event is not used
    dinghy = group
    dict_of_cadets_with_club_dinghies_at_event = list_of_ids_with_groups

    result_dict = {}
    for day in event.days_in_event():
        result_dict[day] = [
            cadet
            for cadet in dict_of_cadets_with_club_dinghies_at_event.list_of_cadets
            if dict_of_cadets_with_club_dinghies_at_event.club_dinghys_for_cadet(
                cadet
            ).has_specific_dinghy_on_day(day=day, dinghy=dinghy)
        ]

    return result_dict

from typing import Dict, List

import pandas as pd

from app.backend.boat_classes.list_of_boat_classes import get_list_of_boat_classes
from app.objects.cadets import Cadet

from app.objects.boat_classes import BoatClass

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_attendance_matrix_for_list_of_cadets_at_event,
)

from app.data_access.store.object_store import ObjectStore

from app.backend.events.summarys import (
    summarise_generic_counts_for_event_over_days_returning_df,
)
from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import DictOfCadetsAndBoatClassAndPartners
from app.objects.day_selectors import Day
from app.objects.events import Event

from app.backend.boat_classes.cadets_with_boat_classes_at_event import (
    get_dict_of_cadets_and_boat_classes_and_partners_at_events,
)


def summarise_class_attendance_for_event(
    object_store: ObjectStore, event: Event
) -> pd.DataFrame:
    dict_of_cadets_and_boat_classes_and_partners_at_events = (
        get_dict_of_cadets_and_boat_classes_and_partners_at_events(
            object_store=object_store, event=event
        )
    )
    list_of_boat_classes = get_list_of_boat_classes(object_store)
    list_of_boat_classes_at_event = (
        dict_of_cadets_and_boat_classes_and_partners_at_events.unique_sorted_list_of_boat_classes_at_event(list_of_boat_classes)
    )
    row_names = list_of_boat_classes_at_event.list_of_names()
    availability_dict = get_attendance_matrix_for_list_of_cadets_at_event(
        object_store=object_store, event=event
    )

    df = summarise_generic_counts_for_event_over_days_returning_df(
        get_id_function=get_relevant_cadet_ids_for_boat_class_id,
        event=event,
        groups=list_of_boat_classes_at_event,
        group_labels=row_names,
        availability_dict=availability_dict,
        list_of_ids_with_groups=dict_of_cadets_and_boat_classes_and_partners_at_events,  ## ignore warning
    )

    return df


def get_relevant_cadet_ids_for_boat_class_id(
    group: BoatClass,
    event: Event,
    list_of_ids_with_groups: DictOfCadetsAndBoatClassAndPartners,
) -> Dict[Day, List[Cadet]]:
    ## map from generic to specific var names. Event is not used
    boat_class = group
    dict_of_cadets_and_boat_classes_and_partners_at_events = list_of_ids_with_groups

    result_dict = {}
    for day in event.days_in_event():
        result_dict[day] = [
            cadet
            for cadet in dict_of_cadets_and_boat_classes_and_partners_at_events.list_of_cadets()
            if dict_of_cadets_and_boat_classes_and_partners_at_events.boat_classes_and_partner_for_cadet(
                cadet
            ).is_in_boat_class_on_day(
                day=day, boat_class=boat_class
            )
        ]

    return result_dict

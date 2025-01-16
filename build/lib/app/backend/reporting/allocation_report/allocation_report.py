from dataclasses import dataclass
from typing import Dict

import pandas as pd

from app.backend.groups.cadets_with_groups_at_event import get_dict_of_cadets_with_groups_at_event
from app.data_access.store.object_store import ObjectStore
from app.objects.exceptions import missing_data
from app.objects.events import Event
from app.objects.composed.cadets_at_event_with_groups import CadetWithGroupOnDay, ListOfCadetsWithGroupOnDay
from app.objects.cadet_with_id_with_group_at_event import GROUP_STR_NAME
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)

all_groups_names = []

specific_parameters_for_allocation_report = SpecificParametersForTypeOfReport(
    #    entry_columns=[CADET_NAME],
    group_by_column=GROUP_STR_NAME,
    report_type="Allocation report",
)


@dataclass
class AdditionalParametersForAllocationReport:
    display_full_names: bool
    include_unallocated_cadets: bool
    add_asterix_for_club_boats: bool

from app.backend.club_boats.cadets_with_club_dinghies_at_event import get_dict_of_cadets_and_club_dinghies_at_event
from app.objects.composed.cadets_at_event_with_club_dinghies import DictOfCadetsAndClubDinghiesAtEvent

def add_club_boat_asterix(
    object_store: ObjectStore, list_of_cadets_with_groups: ListOfCadetsWithGroupOnDay, event: Event
):
    dict_of_cadets_at_event_with_club_dinghies = (
        get_dict_of_cadets_and_club_dinghies_at_event(object_store=object_store, event=event)
    )

    for cadet_with_group in list_of_cadets_with_groups:
        add_club_boat_asterix_to_cadet_with_group_on_day(
            cadet_with_group=cadet_with_group,
            dict_of_cadets_at_event_with_club_dinghies=dict_of_cadets_at_event_with_club_dinghies,
        )

    return list_of_cadets_with_groups


def add_club_boat_asterix_to_cadet_with_group_on_day(
    cadet_with_group: CadetWithGroupOnDay,
    dict_of_cadets_at_event_with_club_dinghies: DictOfCadetsAndClubDinghiesAtEvent
):
    cadet = cadet_with_group.cadet
    day = cadet_with_group.day
    dinghy = dict_of_cadets_at_event_with_club_dinghies.club_dinghys_for_cadet(cadet).dinghy_on_day(day=day, default=missing_data)

    if dinghy is not missing_data:
        cadet_with_group.cadet = cadet_with_group.cadet.add_asterix_to_name()




def get_dict_of_df_for_reporting_allocations_with_flags(
    object_store: ObjectStore,
    event: Event,
    display_full_names: bool = False,
    include_unallocated_cadets: bool = False,
    add_asterix_for_club_boats: bool = True,
) -> Dict[str, pd.DataFrame]:

    group_allocations_data = get_dict_of_cadets_with_groups_at_event(object_store=object_store, event=event)
    dict_of_df = {}
    for day in event.weekdays_in_event():
        list_of_cadets_with_groups = (
            group_allocations_data.get_list_of_cadets_with_group_for_specific_day(
                day=day,
                include_unallocated_cadets=include_unallocated_cadets,
            )
        )
        if add_asterix_for_club_boats:
            list_of_cadets_with_groups = add_club_boat_asterix(
                object_store=object_store,
                list_of_cadets_with_groups=list_of_cadets_with_groups,
                event=event,
            )

        df = list_of_cadets_with_groups.as_df_of_str(
            display_full_names=display_full_names
        )
        dict_of_df[day.name] = df

    return dict_of_df

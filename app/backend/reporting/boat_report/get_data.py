from typing import Dict, Tuple

import pandas as pd

from app.data_access.store.object_store import ObjectStore

from app.backend.reporting.boat_report.boat_report_parameters import *
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_dict_of_all_event_info_for_cadets,
)
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.boat_classes import no_boat_class_partner_or_sail_number

from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets
from app.objects.groups import (
    lake_training_group_location,
    river_training_group_location,
    unallocated_group,
)

from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import Group


def get_dict_of_df_for_boat_report(
    object_store: ObjectStore,
    event: Event,
    additional_parameters: AdditionalParametersForBoatReport,
) -> Dict[str, pd.DataFrame]:
    dict_of_all_event_info_for_cadets = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event, active_only=True
    )
    days_in_event = event.days_in_event()

    dict_of_df = {}
    for day in days_in_event:
        df = get_df_for_day_of_boat_report(
            day=day,
            dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
            additional_parameters=additional_parameters,
        )

        if len(df) > 0:
            dict_of_df[day.name] = df

    return dict_of_df


def get_df_for_day_of_boat_report(
    day: Day,
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets,
    additional_parameters: AdditionalParametersForBoatReport,
) -> pd.DataFrame:
    cadets_at_event_on_day = list_of_active_cadets_on_day(
        day=day, dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets
    )

    list_of_row = [
        row_of_data_for_cadet(
            dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
            cadet=cadet,
            day=day,
            additional_parameters=additional_parameters,
            cadets_at_event_on_day=cadets_at_event_on_day,
        )
        for cadet in cadets_at_event_on_day
        if is_cadet_valid_for_report(
            dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
            cadet=cadet,
            day=day,
            additional_parameters=additional_parameters,
        )
    ]

    df = pd.DataFrame(list_of_row)
    if len(df) == 0:
        return pd.DataFrame()

    df = df.sort_values(by=BOAT_CLASS)

    return df


def list_of_active_cadets_on_day(
    day: Day, dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets
) -> ListOfCadets:
    cadets_at_event_on_day = [
        cadet
        for cadet in dict_of_all_event_info_for_cadets.list_of_cadets
        if dict_of_all_event_info_for_cadets.event_data_for_cadet(
            cadet
        ).registration_data.availability.available_on_day(day)
    ]

    return ListOfCadets(cadets_at_event_on_day)


def row_of_data_for_cadet(
    cadet: Cadet,
    day: Day,
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets,
    additional_parameters: AdditionalParametersForBoatReport,
    cadets_at_event_on_day: ListOfCadets,
) -> pd.Series:
    group = get_group(
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        cadet=cadet,
        day=day,
    )

    first_cadet_name = get_first_cadet_name(
        cadet=cadet,
        additional_parameters=additional_parameters,
    )

    second_cadet_name = get_second_cadet_name_popping_if_required(
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        cadet=cadet,
        day=day,
        additional_parameters=additional_parameters,
        cadets_at_event_on_day=cadets_at_event_on_day,
    )

    (
        boat_class,
        sail_number,
        club_boat_flag,
    ) = get_boat_class_sail_number_and_club_boat_flag(
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        cadet=cadet,
        day=day,
    )

    row_for_cadet = pd.Series(
        {
            FIRST_CADET: first_cadet_name,
            SECOND_CADET: second_cadet_name,
            GROUP: group.name,
            BOAT_CLASS: boat_class,
            SAIL_NUMBER: sail_number,
            CLUB_BOAT: club_boat_flag,
        }
    )

    if additional_parameters.in_out_columns:
        in_out_columns = pd.Series(
            {RAMP: MARKER, LAUNCH: MARKER, IN1: MARKER, OUT1: MARKER, IN2: MARKER}
        )
        row_for_cadet = pd.concat([row_for_cadet, in_out_columns])

    return row_for_cadet


LAUNCH = "Launch"
RAMP = "Ramp"
IN1 = "Return"
OUT1 = "Re-launch"
IN2 = "Final return"

MARKER = " [   ] "


def get_first_cadet_name(
    cadet: Cadet,
    additional_parameters: AdditionalParametersForBoatReport,
) -> str:
    display_full_names = additional_parameters.display_full_names

    if display_full_names:
        first_cadet_name = cadet.name
    else:
        first_cadet_name = cadet.initial_and_surname

    return first_cadet_name


def get_second_cadet_name_popping_if_required(
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets,
    cadet: Cadet,
    day: Day,
    additional_parameters: AdditionalParametersForBoatReport,
    cadets_at_event_on_day: ListOfCadets,  ## we pop from this list to avoid double entry
):
    first_cadet_with_dinghy_and_partner = (
        dict_of_all_event_info_for_cadets.event_data_for_cadet(
            cadet
        ).days_and_boat_class.boat_class_and_partner_on_day(
            day
        )
    )
    no_partner = not first_cadet_with_dinghy_and_partner.has_partner
    if no_partner:
        return ""

    second_cadet = first_cadet_with_dinghy_and_partner.partner_cadet

    display_full_names = additional_parameters.display_full_names
    if display_full_names:
        second_cadet_name = second_cadet.name
    else:
        second_cadet_name = second_cadet.initial_and_surname

    try:  ## avoid double counting
        cadets_at_event_on_day.pop_cadet(second_cadet)
    except:
        pass

    return second_cadet_name


def get_boat_class_sail_number_and_club_boat_flag(
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets,
    cadet: Cadet,
    day: Day,
) -> Tuple[str, str, str]:
    first_cadet_with_dinghy = dict_of_all_event_info_for_cadets.event_data_for_cadet(
        cadet
    ).days_and_boat_class.boat_class_and_partner_on_day(
        day
    )
    boat_name = first_cadet_with_dinghy.boat_class.name[:10]
    sail_number = first_cadet_with_dinghy.sail_number

    has_club_boat = dict_of_all_event_info_for_cadets.dict_of_cadets_and_club_dinghies_at_event.club_dinghys_for_cadet(
        cadet
    ).has_any_dinghy_on_specific_day(
        day=day
    )
    club_boat_flag = "(Club boat)" if has_club_boat else ""

    return boat_name, sail_number, club_boat_flag


def is_cadet_valid_for_report(
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets,
    cadet: Cadet,
    day: Day,
    additional_parameters: AdditionalParametersForBoatReport,
) -> bool:
    group = get_group(
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        cadet=cadet,
        day=day,
    )

    return is_group_valid_for_report(
        group=group, additional_parameters=additional_parameters
    )


def is_group_valid_for_report(
    group: Group, additional_parameters: AdditionalParametersForBoatReport
):
    if additional_parameters.exclude_unallocated_groups:
        if group.is_unallocated:
            return False

    if additional_parameters.exclude_river_training_groups:
        if group.location == river_training_group_location:
            return False

    if additional_parameters.exclude_lake_groups:
        if group.location == lake_training_group_location:
            return False

    return True


def get_group(
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets,
    cadet: Cadet,
    day: Day,
) -> Group:
    group = dict_of_all_event_info_for_cadets.event_data_for_cadet(
        cadet
    ).days_and_groups.group_on_day(day, default=unallocated_group)

    return group

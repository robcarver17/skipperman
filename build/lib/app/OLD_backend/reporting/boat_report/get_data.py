from typing import Dict, List, Tuple

import pandas as pd
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.reporting import (
    AdditionalParametersForBoatReport,
    FIRST_CADET,
    SECOND_CADET,
    GROUP,
    BOAT_CLASS,
    SAIL_NUMBER,
    CLUB_BOAT,
)

from app.objects.groups import (
    lake_training_group_location,
    river_training_group_location,
)
from app.OLD_backend.data.data_for_event import (
    get_data_required_for_event,
    RequiredDataForReport,
)

from app.objects.exceptions import missing_data
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import Group


def get_dict_of_df_for_boat_report(
    interface: abstractInterface,
    event: Event,
    additional_parameters: AdditionalParametersForBoatReport,
) -> Dict[str, pd.DataFrame]:
    data_required = get_data_required_for_event(interface=interface, event=event)
    days_in_event = event.weekdays_in_event()

    if not event.contains_groups:
        additional_parameters.exclude_unallocated_groups = False

    dict_of_df = {}
    for day in days_in_event:
        df = get_df_for_day_of_boat_report(
            day=day,
            data_required=data_required,
            additional_parameters=additional_parameters,
        )

        if len(df) > 0:
            dict_of_df[day.name] = df

    return dict_of_df


def get_df_for_day_of_boat_report(
    day: Day,
    data_required: RequiredDataForReport,
    additional_parameters: AdditionalParametersForBoatReport,
) -> pd.DataFrame:
    cadet_ids_at_event_on_day = list_of_active_cadet_ids_on_day(
        day=day, data_required=data_required
    )

    list_of_row = [
        row_of_data_for_cadet_id(
            cadet_id=cadet_id,
            day=day,
            additional_parameters=additional_parameters,
            data_required=data_required,
            cadet_ids_at_event_on_day=cadet_ids_at_event_on_day,
        )
        for cadet_id in cadet_ids_at_event_on_day
        if is_cadet_id_valid_for_report(
            cadet_id=cadet_id,
            day=day,
            additional_parameters=additional_parameters,
            data_required=data_required,
        )
    ]

    df = pd.DataFrame(list_of_row)
    if len(df) == 0:
        return pd.DataFrame()

    df = df.sort_values(by=BOAT_CLASS)

    return df


def list_of_active_cadet_ids_on_day(
    day: Day, data_required: RequiredDataForReport
) -> List[str]:
    cadet_ids_at_event_on_day = [
        cadet_at_event.cadet_id
        for cadet_at_event in data_required.list_of_cadets_at_event
        if cadet_at_event.availability.available_on_day(day)
        and cadet_at_event.is_active()
    ]

    return cadet_ids_at_event_on_day


def row_of_data_for_cadet_id(
    cadet_id: str,
    day: Day,
    data_required: RequiredDataForReport,
    additional_parameters: AdditionalParametersForBoatReport,
    cadet_ids_at_event_on_day: List[str],
) -> pd.Series:
    group = get_group(cadet_id=cadet_id, data_required=data_required, day=day)

    first_cadet_name = get_first_cadet_name(
        cadet_id=cadet_id,
        data_required=data_required,
        additional_parameters=additional_parameters,
    )

    second_cadet_name = get_second_cadet_name_popping_if_required(
        cadet_id=cadet_id,
        day=day,
        data_required=data_required,
        additional_parameters=additional_parameters,
        cadet_ids_at_event_on_day=cadet_ids_at_event_on_day,
    )

    (
        boat_class,
        sail_number,
        club_boat_flag,
    ) = get_boat_class_sail_number_and_club_boat_flag(
        cadet_id=cadet_id,
        day=day,
        data_required=data_required,
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
    cadet_id: str,
    data_required: RequiredDataForReport,
    additional_parameters: AdditionalParametersForBoatReport,
) -> str:
    display_full_names = additional_parameters.display_full_names
    first_cadet = data_required.list_of_all_cadets.cadet_with_id(cadet_id)
    if display_full_names:
        first_cadet_name = first_cadet.name
    else:
        first_cadet_name = first_cadet.initial_and_surname

    return first_cadet_name


def get_second_cadet_name_popping_if_required(
    cadet_id: str,
    data_required: RequiredDataForReport,
    day: Day,
    additional_parameters: AdditionalParametersForBoatReport,
    cadet_ids_at_event_on_day: List[str],
):
    display_full_names = additional_parameters.display_full_names
    second_cadet_name = ""
    first_cadet_with_dinghy = (
        data_required.list_of_cadets_at_event_with_dinghies.object_with_cadet_id_on_day(
            cadet_id=cadet_id, day=day
        )
    )
    if first_cadet_with_dinghy is not missing_data:
        if first_cadet_with_dinghy.has_partner():
            second_cadet_id = first_cadet_with_dinghy.partner_cadet_id
            second_cadet = data_required.list_of_all_cadets.cadet_with_id(
                second_cadet_id
            )
            if display_full_names:
                second_cadet_name = second_cadet.name
            else:
                second_cadet_name = second_cadet.initial_and_surname

            try:
                cadet_ids_at_event_on_day.remove(second_cadet_id)
            except:
                pass

    return second_cadet_name


def is_cadet_id_valid_for_report(
    cadet_id: str,
    day: Day,
    data_required: RequiredDataForReport,
    additional_parameters: AdditionalParametersForBoatReport,
) -> bool:
    group = get_group(cadet_id=cadet_id, data_required=data_required, day=day)

    return is_group_valid_for_report(
        group=group, additional_parameters=additional_parameters
    )


def get_group(
    cadet_id: str,
    data_required: RequiredDataForReport,
    day: Day,
) -> Group:
    group = data_required.list_of_cadet_ids_with_groups.DO_NOT_USE_group_for_cadet_id_on_day(
        cadet_id=cadet_id, day=day
    )

    return group


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


def get_boat_class_sail_number_and_club_boat_flag(
    cadet_id: str, day: Day, data_required: RequiredDataForReport
) -> Tuple[str, str, str]:
    first_cadet_with_dinghy = (
        data_required.list_of_cadets_at_event_with_dinghies.object_with_cadet_id_on_day(
            cadet_id=cadet_id, day=day
        )
    )
    if first_cadet_with_dinghy is not missing_data:
        boat_class_id = first_cadet_with_dinghy.boat_class_id
        sail_number = first_cadet_with_dinghy.sail_number
        boat_name = data_required.list_of_boat_classes.name_given_id(boat_class_id)
    else:
        boat_name = sail_number = ""

    boat_name = boat_name[:10]

    club_boat_id = data_required.list_of_cadets_at_event_with_club_dinghies.dinghy_for_cadet_id_on_day(
        cadet_id=cadet_id, day=day
    )
    if club_boat_id is missing_data:
        club_boat_flag = ""
    else:
        club_boat_flag = "(Club boat)"

    return boat_name, sail_number, club_boat_flag

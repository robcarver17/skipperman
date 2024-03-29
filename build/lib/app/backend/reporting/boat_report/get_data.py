from typing import Dict, List, Tuple

import pandas as pd

from app.backend.reporting.boat_report.boat_report_parameters import AdditionalParametersForBoatReport, FIRST_CADET, \
    SECOND_CADET, GROUP, BOAT_CLASS, SAIL_NUMBER, CLUB_BOAT

from app.data_access.configuration.configuration import RIVER_TRAINING_GROUP_NAMES, LAKE_TRAINING_GROUP_NAMES
from app.backend.data.data_for_event import get_data_required_for_event, RequiredDataForReport

from app.objects.constants import missing_data
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import UNALLOCATED_GROUP_NAME, Group


def get_dict_of_df_for_boat_report(event: Event, additional_parameters:AdditionalParametersForBoatReport)-> Dict[str, pd.DataFrame]:
    data_required = get_data_required_for_event(event)
    days_in_event = event.weekdays_in_event()

    if not event.contains_groups:
        additional_parameters.exclude_unallocated_groups = False

    dict_of_df = {}
    for day in days_in_event:
        dict_of_df[day.name] = get_df_for_day_of_boat_report(day=day,
                                                             data_required=data_required,
                                                             additional_parameters=additional_parameters)

    return dict_of_df

def get_df_for_day_of_boat_report(day: Day, data_required: RequiredDataForReport, additional_parameters:AdditionalParametersForBoatReport) -> pd.DataFrame:
    cadet_ids_at_event_on_day = list_of_active_cadet_ids_on_day(day=day, data_required=data_required)

    list_of_row = [row_of_data_for_cadet_id(cadet_id=cadet_id,
                                            additional_parameters=additional_parameters,
                                            data_required=data_required,
                                            cadet_ids_at_event_on_day=cadet_ids_at_event_on_day)
                   for cadet_id in cadet_ids_at_event_on_day if
                   is_cadet_id_valid_for_report(cadet_id=cadet_id, additional_parameters=additional_parameters, data_required=data_required)]

    df=pd.DataFrame(list_of_row)

    return df

def list_of_active_cadet_ids_on_day(day: Day, data_required: RequiredDataForReport) -> List[str]:
    cadet_ids_at_event_on_day = [cadet_at_event.cadet_id
                                 for cadet_at_event in data_required.list_of_cadets_at_event
                                 if cadet_at_event.availability.available_on_day(day) and cadet_at_event.is_active()]

    return cadet_ids_at_event_on_day

def row_of_data_for_cadet_id(cadet_id: str,
                             data_required: RequiredDataForReport,
                             additional_parameters:AdditionalParametersForBoatReport,
                             cadet_ids_at_event_on_day: List[str])-> pd.Series:

    group = get_group(cadet_id=cadet_id, data_required=data_required)

    first_cadet_name = get_first_cadet_name(
        cadet_id=cadet_id,
        data_required=data_required,
        additional_parameters=additional_parameters
    )

    second_cadet_name = get_second_cadet_name_popping_if_required(
        cadet_id=cadet_id,
        data_required=data_required,
        additional_parameters=additional_parameters,
        cadet_ids_at_event_on_day=cadet_ids_at_event_on_day
    )

    boat_class, sail_number, club_boat_flag = get_boat_class_sail_number_and_club_boat_flag(cadet_id=cadet_id,
                                                                                            data_required=data_required,
                                                                                    )

    return pd.Series({FIRST_CADET: first_cadet_name,
            SECOND_CADET: second_cadet_name,
            GROUP: group.group_name,
            BOAT_CLASS:boat_class,
            SAIL_NUMBER: sail_number,
            CLUB_BOAT: club_boat_flag})


def get_first_cadet_name(cadet_id: str, data_required: RequiredDataForReport,
                                                    additional_parameters:AdditionalParametersForBoatReport) -> str:
    display_full_names = additional_parameters.display_full_names
    first_cadet = data_required.list_of_all_cadets.cadet_with_id(cadet_id)
    if display_full_names:
        first_cadet_name = first_cadet.name
    else:
        first_cadet_name = first_cadet.initial_and_surname

    return first_cadet_name

def get_second_cadet_name_popping_if_required(cadet_id: str, data_required: RequiredDataForReport,
                                                    additional_parameters:AdditionalParametersForBoatReport,
                                                    cadet_ids_at_event_on_day: List[str]):
    display_full_names = additional_parameters.display_full_names
    second_cadet_name = ""
    first_cadet_with_dinghy = data_required.list_of_cadets_at_event_with_dinghies.object_with_cadet_id(cadet_id)
    if first_cadet_with_dinghy is not missing_data:
        if first_cadet_with_dinghy.has_partner():
            second_cadet_id = first_cadet_with_dinghy.partner_cadet_id
            second_cadet = data_required.list_of_all_cadets.cadet_with_id(second_cadet_id)
            if display_full_names:
                second_cadet_name = second_cadet.name
            else:
                second_cadet_name = second_cadet.initial_and_surname

            try:
                cadet_ids_at_event_on_day.remove(second_cadet_id)
            except:
                pass

    return second_cadet_name



def is_cadet_id_valid_for_report(cadet_id: str, data_required: RequiredDataForReport,
                    additional_parameters:AdditionalParametersForBoatReport
                   ) -> bool:
    group = get_group(cadet_id=cadet_id, data_required=data_required)

    return is_group_valid_for_report(group=group, additional_parameters=additional_parameters)

def get_group(cadet_id: str, data_required: RequiredDataForReport
                   ) -> Group:
    group = data_required.list_of_cadet_ids_with_groups.group_for_cadet_id(cadet_id=cadet_id)

    return group

def is_group_valid_for_report(group: Group, additional_parameters:AdditionalParametersForBoatReport):
    if additional_parameters.exclude_unallocated_groups:
        if group.group_name is UNALLOCATED_GROUP_NAME:
            return False

    if additional_parameters.exclude_river_training_groups:
        if group.group_name in RIVER_TRAINING_GROUP_NAMES:
            return False

    if additional_parameters.exclude_lake_groups:
        if group.group_name in LAKE_TRAINING_GROUP_NAMES:
            return False

    return True

def get_boat_class_sail_number_and_club_boat_flag(cadet_id: str, data_required: RequiredDataForReport) -> Tuple[str,str,str]:

    first_cadet_with_dinghy = data_required.list_of_cadets_at_event_with_dinghies.object_with_cadet_id(cadet_id)
    if first_cadet_with_dinghy is not missing_data:
        boat_class_id = first_cadet_with_dinghy.boat_class_id
        sail_number = first_cadet_with_dinghy.sail_number
        boat_name = data_required.list_of_boat_classes.name_given_id(boat_class_id)
    else:
        boat_name = sail_number = ""

    club_boat_id = data_required.list_of_cadets_at_event_with_club_dinghies.dinghy_for_cadet_id(cadet_id)
    if club_boat_id is missing_data:
        club_boat_flag = ""
    else:
        club_boat_flag = "(Club boat)"

    return boat_name, sail_number, club_boat_flag


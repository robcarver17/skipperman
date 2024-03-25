from typing import List, Dict

import pandas as pd

from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.reporting.boat_report.get_data import get_dict_of_df_for_boat_report
from app.logic.reporting.shared.group_order import  clear_group_order_in_storage
from app.logic.reporting.shared.arrangement_state import clear_arrangement_in_state

from app.backend.reporting.boat_report.boat_report_parameters import  AdditionalParametersForBoatReport

DISPLAY_FULL_NAMES = "display_full_names"
EXCLUDE_LAKE = "exclude_lake"
EXCLUDE_RIVER_TRAIN = "exclude_river_training"
EXCLUDE_UNALLOCATED = "exclude_unallocated"

def get_boat_allocation_report_additional_parameters_from_form_and_save(
    interface: abstractInterface,
):
    parameters = get_boat_report_additional_parameters_from_form(interface)
    save_additional_parameters_for_boat_report(interface, parameters=parameters)


def get_boat_report_additional_parameters_from_form(
    interface: abstractInterface,
) -> AdditionalParametersForBoatReport:
    display_full_names = interface.true_if_radio_was_yes(DISPLAY_FULL_NAMES)
    exclude_unallocated_groups = interface.true_if_radio_was_yes(
        EXCLUDE_UNALLOCATED
    )
    exclude_lake = interface.true_if_radio_was_yes(EXCLUDE_LAKE)
    exclude_river_training_groups = interface.true_if_radio_was_yes(EXCLUDE_RIVER_TRAIN)

    return AdditionalParametersForBoatReport(
        display_full_names=display_full_names,
        exclude_lake_groups=exclude_lake,
        exclude_river_training_groups=exclude_river_training_groups,
        exclude_unallocated_groups=exclude_unallocated_groups

    )


def save_additional_parameters_for_boat_report(
    interface: abstractInterface, parameters: AdditionalParametersForBoatReport
):
    save_show_full_names_parameter(interface=interface, parameters=parameters)
    save_group_exclusion_parameters_and_reset_group_order_and_arrangement_if_required(interface=interface, parameters=parameters)

def save_show_full_names_parameter(interface: abstractInterface, parameters: AdditionalParametersForBoatReport):
    interface.set_persistent_value(DISPLAY_FULL_NAMES, parameters.display_full_names)

def save_group_exclusion_parameters_and_reset_group_order_and_arrangement_if_required(interface: abstractInterface, parameters: AdditionalParametersForBoatReport):

    if any_changes_in_exclusion_pattern(interface=interface, parameters=parameters):
        clear_group_order_in_storage(interface=interface)
        clear_arrangement_in_state(interface=interface)

    save_exclusion_paramters(interface=interface, parameters=parameters)

def any_changes_in_exclusion_pattern(interface: abstractInterface, parameters: AdditionalParametersForBoatReport):
    original_parameters = load_additional_parameters_for_boat_report(interface)

    original_exclusion_of_unallocated = original_parameters.exclude_unallocated_groups
    current_exclusion_of_unallocated = parameters.exclude_unallocated_groups

    original_exclusion_of_lake = original_parameters.exclude_lake_groups
    current_exclusion_of_lake = parameters.exclude_lake_groups

    original_exclusion_of_river_training = original_parameters.exclude_river_training_groups
    current_exclusion_of_river_training = parameters.exclude_river_training_groups

    unallocated_change = original_exclusion_of_unallocated != current_exclusion_of_unallocated
    lake_change = original_exclusion_of_lake != current_exclusion_of_lake
    river_change = original_exclusion_of_river_training != current_exclusion_of_river_training

    return unallocated_change or lake_change or river_change

def save_exclusion_paramters(interface: abstractInterface, parameters: AdditionalParametersForBoatReport):
    interface.set_persistent_value(
        EXCLUDE_UNALLOCATED, parameters.exclude_unallocated_groups
    )
    interface.set_persistent_value(
        EXCLUDE_LAKE, parameters.exclude_lake_groups
    )
    interface.set_persistent_value(
        EXCLUDE_RIVER_TRAIN, parameters.exclude_river_training_groups
    )


def load_additional_parameters_for_boat_report(
    interface: abstractInterface,
) -> AdditionalParametersForBoatReport:

    event =get_event_from_state(interface)
    display_full_names = interface.get_persistent_value(DISPLAY_FULL_NAMES, True)
    exclude_unallocated_groups = interface.get_persistent_value(
        EXCLUDE_UNALLOCATED, True
    )
    exclude_lake_groups = interface.get_persistent_value(EXCLUDE_LAKE, True)
    exclude_river_training_groups = interface.get_persistent_value(EXCLUDE_RIVER_TRAIN, False)

    return AdditionalParametersForBoatReport(exclude_unallocated_groups=exclude_unallocated_groups,
                                             exclude_lake_groups=exclude_lake_groups,
                                             exclude_river_training_groups=exclude_river_training_groups,
                                             display_full_names=display_full_names)

def get_dict_of_df_for_reporting_boats(interface: abstractInterface) -> Dict[str, pd.DataFrame]:
    event = get_event_from_state(interface)
    additional_parameters = load_additional_parameters_for_boat_report(interface)

    dict_of_df = get_dict_of_df_for_boat_report(
        event=event,
        additional_parameters=additional_parameters
    )

    return dict_of_df


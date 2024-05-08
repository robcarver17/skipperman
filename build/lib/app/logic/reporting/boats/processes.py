from typing import List, Dict

import pandas as pd

from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.reporting.boat_report.get_data import get_dict_of_df_for_boat_report

from app.backend.reporting.boat_report.boat_report_parameters import  AdditionalParametersForBoatReport

DISPLAY_FULL_NAMES = "display_full_names"
EXCLUDE_LAKE = "exclude_lake"
EXCLUDE_RIVER_TRAIN = "exclude_river_training"
EXCLUDE_UNALLOCATED = "exclude_unallocated"
INCLUDE_IN_OUT = "include_in_out"

def get_boat_allocation_report_additional_parameters_from_form_and_save(
    interface: abstractInterface,
):
    parameters = get_boat_report_additional_parameters_from_form(interface)
    save_additional_parameters_for_boat_report(interface, parameters=parameters)


def get_boat_report_additional_parameters_from_form(
    interface: abstractInterface,
) -> AdditionalParametersForBoatReport:
    display_full_names = interface.true_if_radio_was_yes(DISPLAY_FULL_NAMES)
    in_out_columms = interface.true_if_radio_was_yes(INCLUDE_IN_OUT)

    exclude_unallocated_groups = interface.true_if_radio_was_yes(
        EXCLUDE_UNALLOCATED
    )
    exclude_lake = interface.true_if_radio_was_yes(EXCLUDE_LAKE)
    exclude_river_training_groups = interface.true_if_radio_was_yes(EXCLUDE_RIVER_TRAIN)

    return AdditionalParametersForBoatReport(
        display_full_names=display_full_names,
        exclude_lake_groups=exclude_lake,
        exclude_river_training_groups=exclude_river_training_groups,
        exclude_unallocated_groups=exclude_unallocated_groups,
        in_out_columns=in_out_columms
    )


def save_additional_parameters_for_boat_report(
    interface: abstractInterface, parameters: AdditionalParametersForBoatReport
):
    save_show_full_names_parameter(interface=interface, parameters=parameters)
    save_include_in_out_parameter(interface=interface, parameters=parameters)
    save_group_exclusion_parameters(interface=interface, parameters=parameters)

def save_show_full_names_parameter(interface: abstractInterface, parameters: AdditionalParametersForBoatReport):
    interface.set_persistent_value(DISPLAY_FULL_NAMES, parameters.display_full_names)

def save_include_in_out_parameter(interface: abstractInterface, parameters: AdditionalParametersForBoatReport):
    interface.set_persistent_value(INCLUDE_IN_OUT, parameters.display_full_names)

def save_group_exclusion_parameters(interface: abstractInterface, parameters: AdditionalParametersForBoatReport):
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
    include_in_out = interface.get_persistent_value(INCLUDE_IN_OUT, True)

    return AdditionalParametersForBoatReport(exclude_unallocated_groups=exclude_unallocated_groups,
                                             exclude_lake_groups=exclude_lake_groups,
                                             exclude_river_training_groups=exclude_river_training_groups,
                                             display_full_names=display_full_names,
                                             in_out_columns=include_in_out)

def get_dict_of_df_for_reporting_boats(interface: abstractInterface) -> Dict[str, pd.DataFrame]:
    event = get_event_from_state(interface)
    additional_parameters = load_additional_parameters_for_boat_report(interface)

    dict_of_df = get_dict_of_df_for_boat_report(
        interface=interface,
        event=event,
        additional_parameters=additional_parameters
    )

    return dict_of_df


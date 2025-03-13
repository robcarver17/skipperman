from typing import Dict

import pandas as pd

from app.backend.reporting.boat_report.boat_report_parameters import (
    AdditionalParametersForBoatReport,
)
from app.backend.reporting.boat_report.get_data import get_dict_of_df_for_boat_report
from app.frontend.reporting.shared.arrangement_state import (
    reset_arrangement_to_default_with_groups_in_data,
)
from app.backend.reporting.report_generator import ReportGenerator
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface

DISPLAY_FULL_NAMES = "display_full_names"
EXCLUDE_LAKE = "exclude_lake"
EXCLUDE_RIVER_TRAIN = "exclude_river_training"
EXCLUDE_UNALLOCATED = "exclude_unallocated"
INCLUDE_IN_OUT = "include_in_out"


def get_boat_allocation_report_additional_parameters_from_form_and_save(
    interface: abstractInterface, report_generator: ReportGenerator
):
    parameters = get_boat_report_additional_parameters_from_form(interface)
    save_additional_parameters_for_boat_report(
        interface, parameters=parameters, report_generator=report_generator
    )


def get_boat_report_additional_parameters_from_form(
    interface: abstractInterface,
) -> AdditionalParametersForBoatReport:
    display_full_names = interface.true_if_radio_was_yes(DISPLAY_FULL_NAMES)
    in_out_columms = interface.true_if_radio_was_yes(INCLUDE_IN_OUT)

    exclude_unallocated_groups = interface.true_if_radio_was_yes(EXCLUDE_UNALLOCATED)
    exclude_lake = interface.true_if_radio_was_yes(EXCLUDE_LAKE)
    exclude_river_training_groups = interface.true_if_radio_was_yes(EXCLUDE_RIVER_TRAIN)

    return AdditionalParametersForBoatReport(
        display_full_names=display_full_names,
        exclude_lake_groups=exclude_lake,
        exclude_river_training_groups=exclude_river_training_groups,
        exclude_unallocated_groups=exclude_unallocated_groups,
        in_out_columns=in_out_columms,
    )


def save_additional_parameters_for_boat_report(
    interface: abstractInterface,
    parameters: AdditionalParametersForBoatReport,
    report_generator: ReportGenerator,
):
    save_show_full_names_parameter(interface=interface, parameters=parameters)
    save_include_in_out_parameter(interface=interface, parameters=parameters)
    save_group_exclusion_parameters(
        interface=interface, parameters=parameters, report_generator=report_generator
    )


def save_show_full_names_parameter(
    interface: abstractInterface, parameters: AdditionalParametersForBoatReport
):
    interface.set_persistent_value(DISPLAY_FULL_NAMES, parameters.display_full_names)


def save_include_in_out_parameter(
    interface: abstractInterface, parameters: AdditionalParametersForBoatReport
):
    interface.set_persistent_value(INCLUDE_IN_OUT, parameters.display_full_names)


def save_group_exclusion_parameters(
    interface: abstractInterface,
    parameters: AdditionalParametersForBoatReport,
    report_generator: ReportGenerator,
):
    exclusion_parameters_changed = have_group_exclusion_parameters_changed(
        interface=interface, parameters=parameters
    )

    interface.set_persistent_value(
        EXCLUDE_UNALLOCATED, parameters.exclude_unallocated_groups
    )
    interface.set_persistent_value(EXCLUDE_LAKE, parameters.exclude_lake_groups)
    interface.set_persistent_value(
        EXCLUDE_RIVER_TRAIN, parameters.exclude_river_training_groups
    )

    if exclusion_parameters_changed:
        interface.log_error(
            "Exclude group settings have changed - resetting arrangement"
        )
        reset_arrangement_to_default_with_groups_in_data(
            interface=interface, report_generator=report_generator
        )


def have_group_exclusion_parameters_changed(
    interface: abstractInterface, parameters: AdditionalParametersForBoatReport
):
    current_paramaters = load_additional_parameters_for_boat_report(interface)
    attr_list = [
        "exclude_unallocated_groups",
        "exclude_lake_groups",
        "exclude_river_training_groups",
    ]
    for attr in attr_list:
        if getattr(current_paramaters, attr) != getattr(parameters, attr):
            return True

    return False


def load_additional_parameters_for_boat_report(
    interface: abstractInterface,
) -> AdditionalParametersForBoatReport:

    display_full_names = interface.get_persistent_value(DISPLAY_FULL_NAMES, True)
    exclude_unallocated_groups = interface.get_persistent_value(
        EXCLUDE_UNALLOCATED, False
    )
    exclude_lake_groups = interface.get_persistent_value(EXCLUDE_LAKE, True)
    exclude_river_training_groups = interface.get_persistent_value(
        EXCLUDE_RIVER_TRAIN, False
    )
    include_in_out = interface.get_persistent_value(INCLUDE_IN_OUT, True)

    return AdditionalParametersForBoatReport(
        exclude_unallocated_groups=exclude_unallocated_groups,
        exclude_lake_groups=exclude_lake_groups,
        exclude_river_training_groups=exclude_river_training_groups,
        display_full_names=display_full_names,
        in_out_columns=include_in_out,
    )


def clear_additional_parameters_for_boat_report(
    interface: abstractInterface,
):
    for parameter_name in [
        DISPLAY_FULL_NAMES,
        EXCLUDE_UNALLOCATED,
        EXCLUDE_RIVER_TRAIN,
        EXCLUDE_LAKE,
        INCLUDE_IN_OUT,
    ]:
        interface.clear_persistent_value(parameter_name)


def get_dict_of_df_for_reporting_boats(
    interface: abstractInterface,
) -> Dict[str, pd.DataFrame]:
    event = get_event_from_state(interface)
    additional_parameters = load_additional_parameters_for_boat_report(interface)

    dict_of_df = get_dict_of_df_for_boat_report(
        object_store=interface.object_store,
        event=event,
        additional_parameters=additional_parameters,
    )

    return dict_of_df

from copy import copy
from typing import Dict

import pandas as pd

from app.frontend.reporting.shared.arrangement_state import (
    reset_arrangement_to_default_with_groups_in_data,
)
from app.backend.reporting.report_generator import ReportGenerator
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import Event

from app.backend.reporting.allocation_report.allocation_report import (
    AdditionalParametersForAllocationReport,
    get_dict_of_df_for_reporting_allocations_with_flags,
)


def get_group_allocation_report_additional_parameters_from_form_and_save(
    interface: abstractInterface, report_generator: ReportGenerator
):
    parameters = get_group_allocation_report_additional_parameters_from_form(interface)
    save_additional_parameters_for_allocation(
        interface, parameters=parameters, report_generator=report_generator
    )


def get_group_allocation_report_additional_parameters_from_form(
    interface: abstractInterface,
) -> AdditionalParametersForAllocationReport:
    display_full_names = interface.true_if_radio_was_yes(SHOW_FULL_NAMES)
    include_unallocated_cadets = interface.true_if_radio_was_yes(
        INCLUDE_UNALLOCATED_CADETS
    )
    add_asterix_for_club_boats = interface.true_if_radio_was_yes(CLUB_BOAT_ASTERIX)

    return AdditionalParametersForAllocationReport(
        display_full_names=display_full_names,
        include_unallocated_cadets=include_unallocated_cadets,
        add_asterix_for_club_boats=add_asterix_for_club_boats,
    )


def save_additional_parameters_for_allocation(
    interface: abstractInterface,
    parameters: AdditionalParametersForAllocationReport,
    report_generator: ReportGenerator,
):
    save_show_full_names_parameter(interface=interface, parameters=parameters)
    save_club_boat_asterix_parameter(interface=interface, parameters=parameters)
    save_unallocated_parameter(
        interface=interface, parameters=parameters, report_generator=report_generator
    )


def save_show_full_names_parameter(
    interface: abstractInterface, parameters: AdditionalParametersForAllocationReport
):
    interface.set_persistent_value(SHOW_FULL_NAMES, parameters.display_full_names)


def save_club_boat_asterix_parameter(
    interface: abstractInterface, parameters: AdditionalParametersForAllocationReport
):
    interface.set_persistent_value(
        CLUB_BOAT_ASTERIX, parameters.add_asterix_for_club_boats
    )


def save_unallocated_parameter(
    interface: abstractInterface,
    parameters: AdditionalParametersForAllocationReport,
    report_generator: ReportGenerator,
):
    original_parameters = load_additional_parameters_for_allocation_report(interface)
    currently_includes_unallocated_cadets = copy(
        original_parameters.include_unallocated_cadets
    )
    change_to_include_unallocated_cadets = parameters.include_unallocated_cadets
    interface.set_persistent_value(
        INCLUDE_UNALLOCATED_CADETS, change_to_include_unallocated_cadets
    )

    if currently_includes_unallocated_cadets != change_to_include_unallocated_cadets:
        interface.log_error(
            "Changed how we are dealing with unallocated cadets: resetting custom group arrangement"
        )
        reset_arrangement_to_default_with_groups_in_data(
            interface=interface, report_generator=report_generator
        )


def load_additional_parameters_for_allocation_report(
    interface: abstractInterface,
) -> AdditionalParametersForAllocationReport:
    display_full_names = interface.get_persistent_value(SHOW_FULL_NAMES, False)
    include_unallocated_cadets = interface.get_persistent_value(
        INCLUDE_UNALLOCATED_CADETS, False
    )
    add_asterix_for_club_boats = interface.get_persistent_value(CLUB_BOAT_ASTERIX, True)

    return AdditionalParametersForAllocationReport(
        display_full_names=display_full_names,
        include_unallocated_cadets=include_unallocated_cadets,
        add_asterix_for_club_boats=add_asterix_for_club_boats,
    )


def clear_additional_parameters_for_allocation_report(
    interface: abstractInterface,
):
    interface.clear_persistent_value(SHOW_FULL_NAMES)
    interface.clear_persistent_value(CLUB_BOAT_ASTERIX)
    interface.clear_persistent_value(INCLUDE_UNALLOCATED_CADETS)


def get_dict_of_df_for_reporting_allocations(
    interface: abstractInterface,
) -> Dict[str, pd.DataFrame]:
    event = get_event_from_state(interface)
    additional_parameters = load_additional_parameters_for_allocation_report(interface)

    dict_of_df = get_dict_of_df_for_reporting_allocations_given_event_and_state(
        interface=interface, event=event, additional_parameters=additional_parameters
    )

    return dict_of_df


def get_dict_of_df_for_reporting_allocations_given_event_and_state(
    interface: abstractInterface,
    event: Event,
    additional_parameters: AdditionalParametersForAllocationReport,
) -> Dict[str, pd.DataFrame]:

    dict_of_df = get_dict_of_df_for_reporting_allocations_with_flags(
        object_store=interface.object_store,
        event=event,
        include_unallocated_cadets=additional_parameters.include_unallocated_cadets,
        display_full_names=additional_parameters.display_full_names,
        add_asterix_for_club_boats=additional_parameters.add_asterix_for_club_boats,
    )

    return dict_of_df


SHOW_FULL_NAMES = "Show_full_names"
INCLUDE_UNALLOCATED_CADETS = "Include unallocated group allocations"
CLUB_BOAT_ASTERIX = "Asterix for club boats"

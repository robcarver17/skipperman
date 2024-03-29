from typing import List, Dict

import pandas as pd

from app.backend.group_allocations.cadet_event_allocations import get_unallocated_cadets, \
    get_list_of_cadets_with_groups, \
    load_allocation_for_event
from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_form import File
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.reporting.shared.group_order import get_group_order_from_stored_or_df, clear_group_order_in_storage
from app.logic.reporting.shared.reporting_options import get_reporting_options
from app.logic.reporting.shared.arrangement_state import clear_arrangement_in_state
from app.objects.events import Event

from app.backend.reporting.allocation_report.allocation_report import (
    specific_parameters_for_allocation_report,
    AdditionalParametersForAllocationReport,
)
from app.backend.reporting.process_stages.create_column_report_from_df import create_column_report_from_df_and_return_filename

def get_group_allocation_report_additional_parameters_from_form_and_save(
    interface: abstractInterface,
):
    parameters = get_group_allocation_report_additional_parameters_from_form(interface)
    save_additional_parameters_for_allocation(interface, parameters=parameters)


def get_group_allocation_report_additional_parameters_from_form(
    interface: abstractInterface,
) -> AdditionalParametersForAllocationReport:
    display_full_names = interface.true_if_radio_was_yes(SHOW_FULL_NAMES)
    include_unallocated_cadets = interface.true_if_radio_was_yes(
        INCLUDE_UNALLOCATED_CADETS
    )

    return AdditionalParametersForAllocationReport(
        display_full_names=display_full_names,
        include_unallocated_cadets=include_unallocated_cadets,
    )


def save_additional_parameters_for_allocation(
    interface: abstractInterface, parameters: AdditionalParametersForAllocationReport
):
    save_show_full_names_parameter(interface=interface, parameters=parameters)
    save_unallocated_parameter_and_reset_group_order_and_arrangement_if_required(interface=interface, parameters=parameters)

def save_show_full_names_parameter(interface: abstractInterface, parameters: AdditionalParametersForAllocationReport):
    interface.set_persistent_value(SHOW_FULL_NAMES, parameters.display_full_names)

def save_unallocated_parameter_and_reset_group_order_and_arrangement_if_required(interface: abstractInterface, parameters: AdditionalParametersForAllocationReport):
    original_parameters = load_additional_parameters_for_allocation_report(interface)
    original_inclusion_of_unallocated = original_parameters.include_unallocated_cadets
    currently_required_unallocated = parameters.include_unallocated_cadets

    if original_inclusion_of_unallocated!=currently_required_unallocated:
        clear_group_order_in_storage(interface=interface)
        clear_arrangement_in_state(interface=interface)

    interface.set_persistent_value(
        INCLUDE_UNALLOCATED_CADETS, parameters.include_unallocated_cadets
    )


def load_additional_parameters_for_allocation_report(
    interface: abstractInterface,
) -> AdditionalParametersForAllocationReport:
    display_full_names = interface.get_persistent_value(SHOW_FULL_NAMES, False)
    include_unallocated_cadets = interface.get_persistent_value(
        INCLUDE_UNALLOCATED_CADETS, False
    )

    return AdditionalParametersForAllocationReport(
        display_full_names=display_full_names,
        include_unallocated_cadets=include_unallocated_cadets,
    )

def get_dict_of_df_for_reporting_allocations(interface: abstractInterface) -> Dict[str, pd.DataFrame]:
    event = get_event_from_state(interface)
    additional_parameters = load_additional_parameters_for_allocation_report(interface)

    dict_of_df = get_dict_of_df_for_reporting_allocations_given_event_and_state(
        event=event,
        additional_parameters=additional_parameters
    )

    return dict_of_df

def get_dict_of_df_for_reporting_allocations_given_event_and_state(event: Event, additional_parameters: AdditionalParametersForAllocationReport)->  Dict[str, pd.DataFrame]:
    dict_of_df = get_dict_of_df_for_reporting_allocations_with_flags(
        event=event,
        include_unallocated_cadets=additional_parameters.include_unallocated_cadets,
        display_full_names=additional_parameters.display_full_names,
    )

    return dict_of_df




def get_dict_of_df_for_reporting_allocations_with_flags(
    event: Event,
    display_full_names: bool = False,
    include_unallocated_cadets: bool = False,
) -> Dict[str, pd.DataFrame]:
    ## NOTE DOESN'T DEAL WITH WAITING LISTS
    ##   is a waiting list cadet unallocated, or allocated with a * against their name?
    ##   at some point report would include club boats

    list_of_cadet_ids_with_groups = load_allocation_for_event(event=event)
    if include_unallocated_cadets:
        unallocated_cadets = get_unallocated_cadets(
            event=event,
            list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
        )
        list_of_cadet_ids_with_groups.add_list_of_unallocated_cadets(unallocated_cadets)

    list_of_cadets_with_groups = get_list_of_cadets_with_groups(
        list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
    )
    df = list_of_cadets_with_groups.to_df_of_str(display_full_names=display_full_names)

    return {"": df}


SHOW_FULL_NAMES = "Show_full_names"
INCLUDE_UNALLOCATED_CADETS = "Include unallocated group_allocations"

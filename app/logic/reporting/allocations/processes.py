import pandas as pd

from app.logic.events.allocation.backend.allocations_data import (
    get_df_for_reporting_allocations_with_flags,
)
from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_form import File
from app.logic.abstract_interface import abstractInterface
from app.logic.reporting.constants import SHOW_FULL_NAMES, INCLUDE_UNALLOCATED_CADETS
from app.logic.reporting.options.group_order import get_group_order_from_stored_or_df
from app.logic.reporting.options.arrangements import get_reporting_options

from app.reporting.allocation_report import (
    specific_parameters_for_allocation_report,
    AdditionalParametersForAllocationReport,
)
from app.reporting.process_stages.create_column_pdf_report_from_df import create_column_pdf_report_from_df_and_return_filename

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
    interface.set_persistent_value(SHOW_FULL_NAMES, parameters.display_full_names)
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


def get_group_order_for_allocation_report(interface: abstractInterface) -> list:
    df = get_df_for_reporting_allocations(interface)
    order_of_groups = get_group_order_from_stored_or_df(
        interface=interface,
        specific_parameters_for_type_of_report=specific_parameters_for_allocation_report,
        df=df,
    )

    return order_of_groups


def get_df_for_reporting_allocations(interface: abstractInterface) -> pd.DataFrame:
    event = get_event_from_state(interface)
    additional_parameters = load_additional_parameters_for_allocation_report(interface)
    df = get_df_for_reporting_allocations_with_flags(
        event=event,
        include_unallocated_cadets=additional_parameters.include_unallocated_cadets,
        display_full_names=additional_parameters.display_full_names,
    )

    return df


def create_report(interface: abstractInterface) -> File:
    print("Creating report")
    df = get_df_for_reporting_allocations(interface)
    reporting_options = get_reporting_options(df=df, specific_parameters_for_type_of_report=specific_parameters_for_allocation_report,
                                           interface=interface)
    print("Reporting options %s" % reporting_options)
    filename = create_column_pdf_report_from_df_and_return_filename(
        reporting_options=reporting_options
    )

    return File(filename)



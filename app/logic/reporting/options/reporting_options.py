import pandas as pd

from app.backend.reporting.options_and_parameters.marked_up_list_from_df_parameters import \
    create_parameters_to_create_marked_up_list_from_df
from app.backend.reporting.options_and_parameters.report_options import ReportingOptions
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import \
    SpecificParametersForTypeOfReport
from app.backend.reporting.process_stages.create_list_of_groups_from_df import get_grouped_df
from app.logic.abstract_interface import abstractInterface
from app.logic.reporting.options.arrangement_state import get_stored_arrangement
from app.logic.reporting.options.group_order import get_group_order_from_stored_or_df
from app.logic.reporting.options.print_options import get_saved_print_options


def augment_order_of_groups_with_sizes(
    reporting_options: ReportingOptions
) -> list:

    grouped_df = get_grouped_df(
        df=reporting_options.df,
        marked_up_list_from_df_parameters=reporting_options.marked_up_list_from_df_parameters,
    )

    sizes = grouped_df.size()

    return ["%s (%d)" % (group, sizes[group]) for group in reporting_options.group_order]


def get_reporting_options(interface: abstractInterface, specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport, df: pd.DataFrame) -> ReportingOptions:
    group_order = get_group_order_from_stored_or_df(
        interface=interface,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
        df=df,
    )
    arrangement_options = get_stored_arrangement(interface)
    print_options = get_saved_print_options(interface=interface, report_type=specific_parameters_for_type_of_report.report_type)

    marked_up_list_from_df_parameters_with_actual_group_order = create_parameters_to_create_marked_up_list_from_df(
        print_options=print_options,
        specific_parameters=specific_parameters_for_type_of_report,
        group_order=group_order
    )

    return ReportingOptions(arrangement=arrangement_options,
                            group_order=group_order,
                            specific_parameters=specific_parameters_for_type_of_report,
                            df=df,
                            print_options=print_options,
                            marked_up_list_from_df_parameters=marked_up_list_from_df_parameters_with_actual_group_order)

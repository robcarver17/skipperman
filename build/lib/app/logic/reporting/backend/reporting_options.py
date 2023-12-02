import pandas as pd
from dataclasses import dataclass
from typing import List

from app.reporting.arrangement.group_order import get_group_order_from_df_given_report_parameters
from app.reporting.options_and_parameters.marked_up_list_from_df_parameters import \
    MarkedUpListFromDfParametersWithActualGroupOrder
from app.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)
from app.reporting.arrangement.arrange_options import ArrangeGroupsOptions
from app.reporting.options_and_parameters.print_options import PrintOptions


### Bring everything together

def adjust_reporting_options_to_reflect_passed_dataframe(
    df: pd.DataFrame, reporting_options_before_adjustment: ReportingOptions
) -> ReportingOptionsForSpecificGroupsInReport:
    list_of_groups_in_df = get_group_order_from_df_given_report_parameters(
        df=df,
        marked_up_list_from_df_parameters=reporting_options_before_adjustment.marked_up_list_from_df,
    )

    marked_up_list_from_df_with_adjusted_groups = adjust_df_parameters_to_reflect_actual_groups_and_add_print_options(
        marked_up_list_from_df_parameters=reporting_options_before_adjustment.marked_up_list_from_df,
        list_of_groups_in_df=list_of_groups_in_df,
        print_options=reporting_options_before_adjustment.print_options,
    )

    return ReportingOptionsForSpecificGroupsInReport(
        marked_up_list_from_df=marked_up_list_from_df_with_adjusted_groups,
        list_of_groups=list_of_groups_in_df,
        print_options=reporting_options_before_adjustment.print_options,
        arrange_groups=reporting_options_before_adjustment.arrange_groups,
    )


def adjust_df_parameters_to_reflect_actual_groups_and_add_print_options(
    marked_up_list_from_df_parameters: SpecificParametersForTypeOfReport,
    print_options: PrintOptions,
    list_of_groups_in_df: list,
) -> MarkedUpListFromDfParametersWithActualGroupOrder:
    ## retains order but only for elements present
    passed_order_of_groups_in_marked_up_list = (
        marked_up_list_from_df_parameters.passed_group_order
    )
    actual_group_order = [
        group
        for group in passed_order_of_groups_in_marked_up_list
        if group in list_of_groups_in_df
    ]

    marked_up_list_from_df_parameters_with_actual_group_order = MarkedUpListFromDfParametersWithActualGroupOrder.from_marked_up_list_and_print_options_with_suggested_group_order(
        actual_group_order=actual_group_order,
        marked_up_list_from_df_parameters=marked_up_list_from_df_parameters,
        print_options=print_options,
    )

    return marked_up_list_from_df_parameters_with_actual_group_order

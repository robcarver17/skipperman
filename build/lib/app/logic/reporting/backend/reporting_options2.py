import pandas as pd

from app.data_access.data import data
from app.logic.reporting.backend.TODELETE import (
    ReportingOptionsForSpecificGroupsInReport,
    ReportingOptions,
    adjust_reporting_options_to_reflect_passed_dataframe,
)
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)
from app.backend.reporting.arrangement.arrange_options import ArrangeGroupsOptions


def get_saved_report_options_bespoke_for_df(
    df: pd.DataFrame,
    report_type: str,
    default_markuplist_from_df_options: SpecificParametersForTypeOfReport,
) -> ReportingOptionsForSpecificGroupsInReport:
    print_options = data.data_print_options.read_for_report(report_type)

    arrange_group_options = ArrangeGroupsOptions()

    reporting_options_before_adjustment = ReportingOptions(
        marked_up_list_from_df=default_markuplist_from_df_options,  ## report specific
        arrange_groups=arrange_group_options,
        print_options=print_options,
    )

    reporting_options = adjust_reporting_options_to_reflect_passed_dataframe(
        df=df, reporting_options_before_adjustment=reporting_options_before_adjustment
    )

    return reporting_options


"""
        Line(["Groups arranged in the following order: %s " % report_options.marked_up_list_from_df.actual_group_order, Button(
            CHANGE_GROUP_ORDER_BUTTON)]),
            Line([
                "Columns arranged in the following way: %s " %  report_options.describe_arrange_groups(),
                Button(CHANGE_GROUP_ARRANGEMENT_BUTTON)]),
"""



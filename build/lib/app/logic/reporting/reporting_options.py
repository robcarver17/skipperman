import pandas as pd

from app.data_access.configuration.configuration import ALL_PAGESIZE, ALL_FONTS
from app.data_access.data import data
from app.logic.abstract_interface import abstractInterface
from app.logic.reporting.backend.TODELETE import (
    ReportingOptionsForSpecificGroupsInReport,
    ReportingOptions,
    adjust_reporting_options_to_reflect_passed_dataframe,
)
from app.reporting.options_and_parameters.marked_up_list_from_df_parameters import \
    MarkedUpListFromDfParametersWithActualGroupOrder
from app.logic.reporting.options.arrangements import save_arrangement
from app.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)
from app.reporting.arrangement.arrangement_order import (
    ArrangementOfColumns,
)
from app.reporting.arrangement.arrange_options import ArrangeGroupsOptions
from app.reporting.options_and_parameters.print_options import PrintOptions
from app.reporting.process_stages.create_list_of_columns_from_groups import (
    create_arrangement_from_list_of_groups_of_marked_up_str,
)
from app.reporting.process_stages.create_list_of_groups_from_df import (
    create_list_of_group_of_marked_up_str_from_df,
    get_grouped_df,
)


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


all_pagesize_as_dict = dict([(pagesize, pagesize) for pagesize in ALL_PAGESIZE])
all_fonts_as_dict = dict([(font, font) for font in ALL_FONTS])


LANDSCAPE = "Landscape"
PORTRAIT = "Portrait"

"""
        Line(["Groups arranged in the following order: %s " % report_options.marked_up_list_from_df.actual_group_order, Button(
            CHANGE_GROUP_ORDER_BUTTON)]),
            Line([
                "Columns arranged in the following way: %s " %  report_options.describe_arrange_groups(),
                Button(CHANGE_GROUP_ARRANGEMENT_BUTTON)]),
"""


def create_arrangement_from_order_and_algo_and_save(
    arrangement_options: ArrangeGroupsOptions,
    current_order: list,
    interface: abstractInterface,
    df: pd.DataFrame,
    marked_up_list_from_df_parameters: SpecificParametersForTypeOfReport,
    print_options: PrintOptions,
) -> ArrangementOfColumns:
    marked_up_list_from_df_parameters_with_actual_group_order = MarkedUpListFromDfParametersWithActualGroupOrder.from_marked_up_list_and_print_options_with_suggested_group_order(
        marked_up_list_from_df_parameters=marked_up_list_from_df_parameters,
        print_options=print_options,
        actual_group_order=current_order,
    )

    report_options = ReportingOptions(
        print_options=print_options,
        marked_up_list_from_df=marked_up_list_from_df_parameters,
        arrange_groups=arrangement_options,
    )

    adjusted_reporting_options = adjust_reporting_options_to_reflect_passed_dataframe(
        reporting_options_before_adjustment=report_options, df=df
    )

    list_of_groups_of_marked_up_str = create_list_of_group_of_marked_up_str_from_df(
        df=df,
        marked_up_list_from_df_parameters=marked_up_list_from_df_parameters_with_actual_group_order,
    )
    arrangement_of_columns = create_arrangement_from_list_of_groups_of_marked_up_str(
        list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
        report_options=adjusted_reporting_options,
    )
    arrangement_options.arrangement_of_columns = arrangement_of_columns
    save_arrangement(interface=interface, arrangement_options=arrangement_options)

    return arrangement_of_columns


def augment_order_of_groups_with_sizes(
    df: pd.DataFrame,
    order_of_groups: list,
    marked_up_list_from_df_parameters: SpecificParametersForTypeOfReport,
    print_options: PrintOptions,
) -> list:
    marked_up_list_from_df_parameters_with_actual_group_order = MarkedUpListFromDfParametersWithActualGroupOrder.from_marked_up_list_and_print_options_with_suggested_group_order(
        marked_up_list_from_df_parameters=marked_up_list_from_df_parameters,
        print_options=print_options,
        actual_group_order=order_of_groups,
    )
    grouped_df = get_grouped_df(
        df=df,
        marked_up_list_from_df_parameters=marked_up_list_from_df_parameters_with_actual_group_order,
    )

    sizes = grouped_df.size()

    return ["%s (%d)" % (group, size) for group, size in zip(order_of_groups, sizes)]

import os
import datetime
import pandas as pd
from app.logic.data import DataAndInterface
from app.interface import (
    ReportingOptions,
    ReportingOptionsForSpecificGroupsInReport,
    PrintOptions,
    ArrangeGroupsOptions,
    MarkedUpListFromDfParameters,
    adjust_reporting_options_to_reflect_passed_dataframe,
    describe_arrangement,
    ARRANGE_PASSED_LIST,
    POSSIBLE_ARRANGEMENTS,
)
from app.data_access.configuration.configuration import ALL_PAGESIZE, ALL_FONTS


def get_default_path_and_filename(default_path: str, default_title: str) -> str:

    default_file_name = default_title.replace(" ", "_")
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    default_file_name = "%s_%s.pdf" % (default_file_name, timestamp)

    default_path_and_filename = os.path.join(default_path, default_file_name)

    return default_path_and_filename


def get_default_report_options(
    df: pd.DataFrame,
    default_path_and_filename: str,
    default_title: str,
    default_markuplist_from_df_options: MarkedUpListFromDfParameters,
) -> ReportingOptionsForSpecificGroupsInReport:

    print_options = PrintOptions(
        path_and_filename=default_path_and_filename,
        title_str=default_title,
    )

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



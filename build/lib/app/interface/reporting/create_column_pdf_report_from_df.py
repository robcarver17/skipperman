import pandas as pd

from app.logic.reporting.backend import (
    ReportingOptionsForSpecificGroupsInReport,
)
from app.logic.reporting.backend import (
    create_list_of_group_of_marked_up_str_from_df,
)
from app.logic.reporting.backend import (
    create_columns_from_list_of_groups_of_marked_up_str,
)
from app.logic.reporting.backend import (
    create_pdf_from_list_of_columns_and_return_filename,
)


def create_column_pdf_report_from_df_and_return_filename(
    df: pd.DataFrame, report_options: ReportingOptionsForSpecificGroupsInReport
) -> str:
    list_of_groups_of_marked_up_str = create_list_of_group_of_marked_up_str_from_df(
        df=df, report_options=report_options
    )
    list_of_columns = create_columns_from_list_of_groups_of_marked_up_str(
        list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
        report_options=report_options,
    )
    filename = create_pdf_from_list_of_columns_and_return_filename(
        list_of_columns=list_of_columns, report_options=report_options
    )

    return filename

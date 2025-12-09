from app.backend.reporting.process_stages.create_list_of_groups_from_df import (
    create_list_of_pages_from_dict_of_df,
)
from app.backend.reporting.process_stages.create_list_of_columns_from_groups import (
    create_list_of_pages_with_columns_from_list_of_pages,
)
from app.backend.reporting.process_stages.create_file_from_list_of_columns import (
    create_report_from_list_of_columns_and_return_filename,
)
from app.backend.reporting.options_and_parameters.report_options import (
    ReportingOptions,
)


def create_column_report_from_df_and_return_filename(
    reporting_options: ReportingOptions,
) -> str:
    list_of_pages = create_list_of_pages_from_dict_of_df(
        dict_of_df=reporting_options.dict_of_df,
        reporting_options=reporting_options,
    )
    list_of_pages_with_columns = create_list_of_pages_with_columns_from_list_of_pages(
        list_of_pages=list_of_pages, reporting_options=reporting_options
    )
    filename = create_report_from_list_of_columns_and_return_filename(
        list_of_pages_with_columns=list_of_pages_with_columns,
        reporting_options=reporting_options,
    )

    return filename

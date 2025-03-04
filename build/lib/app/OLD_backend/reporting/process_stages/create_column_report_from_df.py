from app.backend.reporting import (
    create_list_of_pages_from_dict_of_df,
)
from app.backend.reporting import (
    create_list_of_pages_with_columns_from_list_of_pages,
)
from app.backend.reporting import (
    create_report_from_list_of_columns_and_return_filename,
)
from app.backend.reporting import (
    ReportingOptions,
)


def create_column_report_from_df_and_return_filename(
    reporting_options: ReportingOptions,
) -> str:
    list_of_pages = create_list_of_pages_from_dict_of_df(
        dict_of_df=reporting_options.dict_of_df,
        marked_up_list_from_df_parameters=reporting_options.marked_up_list_from_df_parameters,
    )
    list_of_pages_with_columns = create_list_of_pages_with_columns_from_list_of_pages(
        list_of_pages=list_of_pages, reporting_options=reporting_options
    )
    filename = create_report_from_list_of_columns_and_return_filename(
        list_of_pages_with_columns=list_of_pages_with_columns,
        reporting_options=reporting_options,
    )

    return filename

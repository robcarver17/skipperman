import os
from typing import Dict

import pandas as pd
from app.OLD_backend.reporting.options_and_parameters.print_options import PrintOptions

from app.OLD_backend.reporting.process_stages.create_dict_of_df_from_list_of_pages_with_columns import (
    convert_list_of_pages_with_columns_to_dict_of_df,
)
from app.OLD_backend.reporting.process_stages.strings_columns_groups import (
    ListOfPagesWithColumns,
)
from app.OLD_backend.reporting.process_stages.pdf_layout import PdfLayout
from app.OLD_backend.reporting.options_and_parameters.report_options import (
    ReportingOptions,
)
from app.data_access.file_access import download_directory, public_reporting_directory
from app.data_access.xls_and_csv import save_dict_of_df_as_spreadsheet_file


def create_report_from_list_of_columns_and_return_filename(
    list_of_pages_with_columns: ListOfPagesWithColumns,
    reporting_options: ReportingOptions,
) -> str:
    print_options = reporting_options.print_options

    if print_options.output_pdf:
        filename = create_pdf_report_from_list_of_columns_and_return_filename(
            list_of_pages_with_columns=list_of_pages_with_columns,
            reporting_options=reporting_options,
        )
    else:
        filename = create_csv_report_from_list_of_columns_and_return_filename(
            list_of_pages_with_columns=list_of_pages_with_columns,
            reporting_options=reporting_options,
        )

    return filename


def create_pdf_report_from_list_of_columns_and_return_filename(
    list_of_pages_with_columns: ListOfPagesWithColumns,
    reporting_options: ReportingOptions,
):
    print_options = reporting_options.print_options

    pdf_layout = PdfLayout(print_options=print_options)

    for page in list_of_pages_with_columns:
        pdf_layout.add_page(page)

    path_and_filename = get_path_and_filename_for_report(print_options, ".pdf")
    pdf_layout.output_file(path_and_filename)

    return path_and_filename


def create_csv_report_from_list_of_columns_and_return_filename(
    list_of_pages_with_columns: ListOfPagesWithColumns,
    reporting_options: ReportingOptions,
):
    dict_of_df = convert_list_of_pages_with_columns_to_dict_of_df(
        list_of_pages_with_columns
    )
    path_and_filename_with_extension = (
        create_csv_report_from_dict_of_df_and_return_filename(
            dict_of_df=dict_of_df, print_options=reporting_options.print_options
        )
    )

    return path_and_filename_with_extension


def create_csv_report_from_dict_of_df_and_return_filename(
    dict_of_df: Dict[str, pd.DataFrame],
    print_options: PrintOptions,
):
    path_and_filename_no_extension = get_path_and_filename_for_report(
        print_options, use_extension=""
    )
    path_and_filename_with_extension = save_dict_of_df_as_spreadsheet_file(
        dict_of_df=dict_of_df,
        path_and_filename_no_extension=path_and_filename_no_extension,
    )

    return path_and_filename_with_extension


def get_path_and_filename_for_report(
    print_options: PrintOptions, use_extension: str = ".pdf"
):
    filename = print_options.filename + use_extension
    public = print_options.publish_to_public
    reporting_directory = public_reporting_directory if public else download_directory
    path_and_filename = os.path.join(reporting_directory, filename)

    return path_and_filename

from typing import Dict

import pandas as pd
from app.backend.reporting.options_and_parameters.print_options import PrintOptions

from app.backend.reporting.process_stages.create_dict_of_df_from_list_of_pages_with_columns import (
    convert_list_of_pages_with_columns_to_dict_of_df,
)
from app.backend.reporting.process_stages.strings_columns_groups import (
    ListOfPagesWithColumns,
)
from app.backend.reporting.process_stages.pdf_layout import PdfLayout
from app.backend.reporting.options_and_parameters.report_options import (
    ReportingOptions,
)
from app.data_access.configuration.configuration import (
    HOMEPAGE,
    PUBLIC_REPORTING_SUBDIRECTORY,
)
from app.data_access.file_access import (
    PathAndFilename,
    delete_all_files_matching_filename,
    web_pathname_of_public_version_of_local_file_without_extension,
    get_public_filename_given_local_file,
    add_suffix_to_public_filename,
)
from app.data_access.init_directories import (
    public_reporting_directory,
    download_directory,
)
from app.data_access.xls_and_csv import save_dict_of_df_as_spreadsheet_file
from shutil import copy2 as copy_file


def create_report_from_list_of_columns_and_return_filename(
    list_of_pages_with_columns: ListOfPagesWithColumns,
    reporting_options: ReportingOptions,
) -> str:
    print_options = reporting_options.print_options

    if print_options.output_pdf:
        path_and_filename = create_pdf_report_from_list_of_columns_and_return_filename(
            list_of_pages_with_columns=list_of_pages_with_columns,
            reporting_options=reporting_options,
        )
    else:
        path_and_filename = create_csv_report_from_list_of_columns_and_return_filename(
            list_of_pages_with_columns=list_of_pages_with_columns,
            reporting_options=reporting_options,
        )

    public = print_options.publish_to_public
    if public:
        publish_report_to_public(path_and_filename)

    return path_and_filename.full_path_and_name


def create_pdf_report_from_list_of_columns_and_return_filename(
    list_of_pages_with_columns: ListOfPagesWithColumns,
    reporting_options: ReportingOptions,
) -> PathAndFilename:
    print_options = reporting_options.print_options

    pdf_layout = PdfLayout(print_options=print_options)

    for page in list_of_pages_with_columns:
        if len(page) == 0:
            continue
        pdf_layout.add_page(page)

    path_and_filename = get_download_path_and_filename_for_report(print_options, "pdf")
    pdf_layout.output_file(path_and_filename.full_path_and_name)

    return path_and_filename


def create_csv_report_from_list_of_columns_and_return_filename(
    list_of_pages_with_columns: ListOfPagesWithColumns,
    reporting_options: ReportingOptions,
) -> PathAndFilename:
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
) -> PathAndFilename:
    path_and_filename_no_extension = get_download_path_and_filename_for_report(
        print_options, use_extension=""
    )
    path_and_filename_with_extension = save_dict_of_df_as_spreadsheet_file(
        dict_of_df=dict_of_df,
        path_and_filename_no_extension=path_and_filename_no_extension,
    )

    return path_and_filename_with_extension


def web_pathname_of_public_version_of_local_report_file(print_options: PrintOptions):
    local_file = get_download_path_and_filename_for_report(print_options)
    return web_pathname_of_public_version_of_local_file_without_extension(
        path_and_filename=local_file,
        public_path=PUBLIC_REPORTING_SUBDIRECTORY,
        webserver_url=HOMEPAGE,
    )


def get_download_path_and_filename_for_report(
    print_options: PrintOptions, use_extension: str = "pdf"
):
    return PathAndFilename(
        path=download_directory,
        filename_without_extension=print_options.filename,
        extension=use_extension,
    )


def publish_report_to_public(download_path_and_filename: PathAndFilename):
    delete_existing_public_files(download_path_and_filename)
    copy_local_file_to_public_directory(download_path_and_filename)


def delete_existing_public_files(download_path_and_filename: PathAndFilename):
    delete_all_files_matching_filename(
        filename=download_path_and_filename.filename_without_extension,
        pathname=public_reporting_directory,
    )


def copy_local_file_to_public_directory(local_path_and_filename: PathAndFilename):
    input_path_and_filename_as_str = local_path_and_filename.full_path_and_name
    output_path_and_filename = get_public_filename_with_suffix_given_local_file(
        local_path_and_filename
    )
    output_path_and_filename_as_str = output_path_and_filename.full_path_and_name

    copy_file(input_path_and_filename_as_str, output_path_and_filename_as_str)


def get_public_filename_with_suffix_given_local_file(
    local_path_and_filename: PathAndFilename,
) -> PathAndFilename:
    output_path_and_filename = get_public_filename_given_local_file(
        local_path_and_filename, public_path=public_reporting_directory
    )
    add_suffix_to_public_filename(output_path_and_filename)

    return output_path_and_filename

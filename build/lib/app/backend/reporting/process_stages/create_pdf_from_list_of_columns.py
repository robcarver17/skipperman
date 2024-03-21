import os

from app.data_access.configuration.configuration import REPORTING_SUBDIRECTORY
from app.backend.reporting.process_stages.strings_columns_groups import PageWithColumns, ListOfPagesWithColumns
from app.backend.reporting.process_stages.pdf_layout import PdfLayout, add_page_contents_to_pdf_layout
from app.backend.reporting.options_and_parameters.report_options import ReportingOptions

home_directory = os.path.expanduser("~")
reporting_directory = os.path.join(home_directory, REPORTING_SUBDIRECTORY)
try:
    os.mkdir(reporting_directory)
except:
    pass

def create_report_from_list_of_columns_and_return_filename(
    list_of_pages_with_columns: ListOfPagesWithColumns,
    reporting_options: ReportingOptions,
) -> str:
    print_options = reporting_options.print_options

    if print_options.output_pdf:
        filename = create_pdf_report_from_list_of_columns_and_return_filename(
            list_of_pages_with_columns=list_of_pages_with_columns,
            reporting_options=reporting_options
        )
    else:
        filename = create_csv_report_from_list_of_columns_and_return_filename(
            list_of_pages_with_columns=list_of_pages_with_columns,
            reporting_options=reporting_options
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

    path_and_filename = get_path_and_filename(reporting_options)
    pdf_layout.output_file(path_and_filename)

    return path_and_filename


def create_csv_report_from_list_of_columns_and_return_filename(
        list_of_pages_with_columns: ListOfPagesWithColumns,
        reporting_options: ReportingOptions,
):
    print_options = reporting_options.print_options

    pdf_layout = PdfLayout(print_options=print_options)

    for page in list_of_pages_with_columns:
        pdf_layout.add_page(page)

    path_and_filename = get_path_and_filename(reporting_options)

    return path_and_filename

def get_path_and_filename(reporting_options: ReportingOptions):
    print_options = reporting_options.print_options
    filename = print_options.filename_with_extension
    path_and_filename = os.path.join(reporting_directory, filename)

    return path_and_filename
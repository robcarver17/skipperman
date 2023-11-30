from app.interface import ListtOfColumns
from app.logic.reporting.backend import PdfLayout
from app.interface import (
    ReportingOptionsForSpecificGroupsInReport,
)


def create_pdf_from_list_of_columns_and_return_filename(
    list_of_columns: ListtOfColumns,
    report_options: ReportingOptionsForSpecificGroupsInReport,
):
    print_options = report_options.print_options
    pdf_layout = PdfLayout(list_of_columns=list_of_columns, print_options=print_options)

    pdf_layout.add_page()
    pdf_layout.add_title_to_page()

    for column_number, column in enumerate(list_of_columns):
        line_number = 0
        for group in column:
            for marked_up_text in group:
                pdf_layout.put_text_on_page(
                    column_number=column_number,
                    line_number=line_number,
                    marked_up_text=marked_up_text,
                )
                line_number += 1

            ## end of group, add extra line
            line_number += 1

    path_and_filename = print_options.filename
    pdf_layout.output_file(path_and_filename)

    return path_and_filename

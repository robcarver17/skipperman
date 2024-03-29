import numpy as np

from app.backend.reporting.process_stages.optimise_column_layout import (
    _generate_list_of_all_possible_indices,
    _find_best_list_of_indices,
)
from app.backend.reporting.process_stages.strings_columns_groups import (
    PageWithColumns,
    create_list_of_pages_with_columns_from_list_of_pages_and_arrangements, ListOfPages, Page, ListOfPagesWithColumns,
)
from app.backend.reporting.arrangement.arrangement_order import (
    ArrangementOfColumns, ListOfArrangementOfColumns,
)
from app.backend.reporting.options_and_parameters.report_options import ReportingOptions
from app.backend.reporting.arrangement.arrangement_methods import (
    ARRANGE_OPTIMISE,
    ARRANGE_PASSED_LIST,
    ARRANGE_RECTANGLE,
)
from app.backend.reporting.options_and_parameters.print_options import PrintOptions

def create_list_of_pages_with_columns_from_list_of_pages(list_of_pages: ListOfPages,
                                      reporting_options: ReportingOptions) -> ListOfPagesWithColumns:
    list_of_arrangement_of_columns = create_arrangement_from_list_of_pages(list_of_pages=list_of_pages,
                                                                   reporting_options=reporting_options)

    list_of_pages_with_columns =  create_list_of_pages_with_columns_from_list_of_pages_and_arrangements(
        list_of_pages=list_of_pages,
        list_of_arrangement_of_columns=list_of_arrangement_of_columns,
    )

    return list_of_pages_with_columns


def create_arrangement_from_list_of_pages(list_of_pages: ListOfPages,
                                          reporting_options: ReportingOptions) -> ListOfArrangementOfColumns:

    list_of_arrangements_of_columns = [
        create_arrangement_from_pages(page, reporting_options=reporting_options)
        for page in list_of_pages
    ]

    return ListOfArrangementOfColumns(list_of_arrangements_of_columns)

def create_arrangement_from_pages(page: Page,
                                              reporting_options: ReportingOptions) -> ArrangementOfColumns:

    arrangement_options = reporting_options.arrangement
    print_options = reporting_options.print_options

    arrangement_method = arrangement_options.arrangement_method
    if arrangement_method is ARRANGE_PASSED_LIST:
        return arrangement_options.arrangement_of_columns

    elif arrangement_method is ARRANGE_RECTANGLE:
        return get_order_of_indices_even_sizing(
            page=page,
            print_options=print_options,
        )

    elif arrangement_method is ARRANGE_OPTIMISE:
        return get_optimal_size_indices(
            print_options=print_options,
            page=page,
        )
    else:
        raise Exception("Arrangement %s not recognised" % arrangement_method)


def get_order_of_indices_even_sizing(
    page: Page,
    print_options: PrintOptions,
) -> ArrangementOfColumns:
    landscape = print_options.landscape
    group_count = len(page)

    return get_order_of_indices_even_sizing_with_parameters(
        group_count=group_count, landscape=landscape
    )


def get_order_of_indices_even_sizing_with_parameters(
    group_count: int, landscape: bool = True
) -> ArrangementOfColumns:
    long_side_column_count = (group_count * (2**0.5)) ** 0.5
    short_side_column_count = group_count / long_side_column_count
    if landscape:
        number_of_columns = int(np.ceil(long_side_column_count))
    else:
        number_of_columns = int(np.ceil(short_side_column_count))

    column_length = int(np.ceil(group_count / number_of_columns))

    def _potentially_truncated_list(column_number):
        full_list = range(
            column_number * column_length, (column_number + 1) * column_length
        )
        truncated_list = [x for x in full_list if x < group_count]

        return truncated_list

    order_list_of_indices = list(
        [
            _potentially_truncated_list(column_number)
            for column_number in range(number_of_columns)
        ]
    )

    return ArrangementOfColumns(order_list_of_indices)


def get_optimal_size_indices(
    print_options: PrintOptions,
    page: Page,
) -> ArrangementOfColumns:
    ## want to get ratio as close as possible to h/w ratio which will come from paper size
    ## generate all possible combinations and test

    group_count = len(page)
    series_of_possible_indices = _generate_list_of_all_possible_indices(group_count)

    best_list_of_indices = _find_best_list_of_indices(
        series_of_possible_indices=series_of_possible_indices,
        page=page,
        print_options=print_options,
    )

    return ArrangementOfColumns(best_list_of_indices)

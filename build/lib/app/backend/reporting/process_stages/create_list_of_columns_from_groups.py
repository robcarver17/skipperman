from typing import List

import numpy as np
from app.backend.reporting.arrangement.arrange_options import ArrangementOptionsAndGroupOrder

from app.backend.reporting.process_stages.optimise_column_layout import (
    _generate_list_of_all_possible_indices,
    _find_best_list_of_indices,
)
from app.backend.reporting.process_stages.strings_columns_groups import (
    create_list_of_pages_with_columns_from_list_of_pages_and_arrangement_options, ListOfPages, Page, ListOfPagesWithColumns,
)
from app.backend.reporting.arrangement.arrangement_order import (
    ArrangementOfColumns)
from app.backend.reporting.options_and_parameters.report_options import ReportingOptions
from app.backend.reporting.arrangement.arrangement_methods import (
    ARRANGE_PASSED_LIST,
    ARRANGE_RECTANGLE,
)
from app.backend.reporting.options_and_parameters.print_options import PrintOptions

def create_list_of_pages_with_columns_from_list_of_pages(list_of_pages: ListOfPages,
                                      reporting_options: ReportingOptions) -> ListOfPagesWithColumns:
    arrangement_options_and_group_order = modify_arrangement_given_list_of_pages_and_method(list_of_pages=list_of_pages,
                                                                                            reporting_options=reporting_options)

    list_of_pages_with_columns =  create_list_of_pages_with_columns_from_list_of_pages_and_arrangement_options(
        list_of_pages=list_of_pages,
        arrangement_options_and_group_order=arrangement_options_and_group_order,
    )

    return list_of_pages_with_columns


def modify_arrangement_given_list_of_pages_and_method(list_of_pages: ListOfPages,
                                                      reporting_options: ReportingOptions) -> ArrangementOptionsAndGroupOrder:

    unique_list_of_groups_across_all_pages= list_of_pages.unique_list_of_groups_across_all_pages()

    arrangement_options_and_group_order = reporting_options.arrange_options_and_group_order
    arrangement_options = arrangement_options_and_group_order.arrangement_options
    arrangement_method = arrangement_options.arrangement_method

    print(arrangement_method)
    if arrangement_method is ARRANGE_PASSED_LIST:
        arrangement_of_columns = arrangement_options.arrangement_of_columns

    elif arrangement_method ==ARRANGE_RECTANGLE:
        print_options = reporting_options.print_options
        arrangement_of_columns = get_order_of_indices_even_sizing(
            unique_list_of_groups_across_all_pages=unique_list_of_groups_across_all_pages,
            print_options=print_options,
        )

    else:
        raise Exception("Arrangement %s not recognised" % arrangement_method)

    arrangement_options_and_group_order.replace_column_arrangement(arrangement_of_columns)

    return arrangement_options_and_group_order

def get_order_of_indices_even_sizing(
    unique_list_of_groups_across_all_pages: List[str],
    print_options: PrintOptions,
) -> ArrangementOfColumns:
    landscape = print_options.landscape
    group_count = len(unique_list_of_groups_across_all_pages)

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
    print("optimisting....")
    group_count = len(page)
    series_of_possible_indices = _generate_list_of_all_possible_indices(group_count)
    print("Consider %d options" % len(series_of_possible_indices))
    best_list_of_indices = _find_best_list_of_indices(
        series_of_possible_indices=series_of_possible_indices,
        page=page,
        print_options=print_options,
    )

    return ArrangementOfColumns(best_list_of_indices)

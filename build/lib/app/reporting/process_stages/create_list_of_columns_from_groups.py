import numpy as np

from app.reporting.process_stages.optimise_column_layout import (
    _generate_list_of_all_possible_indices,
    _find_best_list_of_indices,
)
from app.reporting.process_stages.strings_columns_groups import (
    ListtOfColumns,
    ListOfGroupsOfMarkedUpStrings,
    create_columns_from_list_of_groups_of_marked_up_str_with_passed_list,
)
from app.reporting.arrangement.arrangement_order import (
    ArrangementOfColumns,
)
from app.reporting.options_and_parameters.report_options import ReportingOptions
from app.reporting.arrangement.arrangement_methods import (
    ARRANGE_OPTIMISE,
    ARRANGE_PASSED_LIST,
    ARRANGE_RECTANGLE,
)
from app.reporting.options_and_parameters.print_options import PrintOptions

def create_columns_from_list_of_groups_of_marked_up_str(
    list_of_groups_of_marked_up_str: ListOfGroupsOfMarkedUpStrings,
        reporting_options: ReportingOptions
) -> ListtOfColumns:
    arrangement_of_columns = create_arrangement_from_list_of_groups_of_marked_up_str(
        list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
        reporting_options=reporting_options
    )

    return create_columns_from_list_of_groups_of_marked_up_str_with_passed_list(
        list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
        arrangement_of_columns=arrangement_of_columns,
    )


def create_arrangement_from_list_of_groups_of_marked_up_str(
    list_of_groups_of_marked_up_str: ListOfGroupsOfMarkedUpStrings,
    reporting_options: ReportingOptions
) -> ArrangementOfColumns:
    arrangement_options = reporting_options.arrangement
    print_options = reporting_options.print_options

    arrangement_method = arrangement_options.arrangement_method
    if arrangement_method is ARRANGE_PASSED_LIST:
        return arrangement_options.arrangement_of_columns

    elif arrangement_method is ARRANGE_RECTANGLE:
        return get_order_of_indices_even_sizing(
            list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
            print_options=print_options,
        )

    elif arrangement_method is ARRANGE_OPTIMISE:
        return get_optimal_size_indices(
            print_options=print_options,
            list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
        )
    else:
        raise Exception("Arrangement %s not recognised" % arrangement_method)




def get_order_of_indices_even_sizing(
    list_of_groups_of_marked_up_str: ListOfGroupsOfMarkedUpStrings,
    print_options: PrintOptions,
) -> ArrangementOfColumns:
    landscape = print_options.landscape
    group_count = len(list_of_groups_of_marked_up_str)

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
    list_of_groups_of_marked_up_str: ListOfGroupsOfMarkedUpStrings,
) -> ArrangementOfColumns:
    ## want to get ratio as close as possible to h/w ratio which will come from paper size
    ## generate all possible combinations and test

    group_count = len(list_of_groups_of_marked_up_str)
    series_of_possible_indices = _generate_list_of_all_possible_indices(group_count)

    best_list_of_indices = _find_best_list_of_indices(
        series_of_possible_indices=series_of_possible_indices,
        list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
        print_options=print_options,
    )

    return ArrangementOfColumns(best_list_of_indices)

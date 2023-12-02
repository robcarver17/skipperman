import numpy as np

from app.interface import (
    _generate_list_of_all_possible_indices,
    _find_best_list_of_indices,
)
from app.interface import (
    ListtOfColumns,
    ListOfGroupsOfMarkedUpStrings,
    _create_columns_from_list_of_groups_of_marked_up_str_with_passed_list,
)
from app.interface import (
    ReportingOptionsForSpecificGroupsInReport,
    ARRANGE_OPTIMISE,
    ARRANGE_PASSED_LIST,
    ARRANGE_RECTANGLE,
)


def create_columns_from_list_of_groups_of_marked_up_str(
    list_of_groups_of_marked_up_str: ListOfGroupsOfMarkedUpStrings,
    report_options: ReportingOptionsForSpecificGroupsInReport,
) -> ListtOfColumns:

    arrangement = report_options.arrange_groups.arrangement

    if arrangement is ARRANGE_PASSED_LIST:
        return _create_columns_from_list_of_groups_of_marked_up_str_forced_order(
            list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
            report_options=report_options,
        )
    elif arrangement is ARRANGE_RECTANGLE:
        return _create_columns_from_list_of_groups_of_marked_up_str_evenly_size(
            list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
            report_options=report_options,
        )
    elif arrangement is ARRANGE_OPTIMISE:
        return _create_columns_from_list_of_groups_of_marked_up_str_optimise_size(
            list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
            report_options=report_options,
        )
    else:
        raise Exception("Arrangement %s not recognised" % arrangement)


def _create_columns_from_list_of_groups_of_marked_up_str_evenly_size(
    list_of_groups_of_marked_up_str: ListOfGroupsOfMarkedUpStrings,
    report_options: ReportingOptionsForSpecificGroupsInReport,
) -> ListtOfColumns:

    landscape = report_options.landscape
    group_count = len(list_of_groups_of_marked_up_str)

    order_list_of_indices = _get_order_of_indices_even_sizing(
        group_count=group_count, landscape=landscape
    )

    return _create_columns_from_list_of_groups_of_marked_up_str_with_passed_list(
        list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
        order_list_of_indices=order_list_of_indices,
    )


def _get_order_of_indices_even_sizing(group_count: int, landscape: bool = True) -> list:
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

    return order_list_of_indices


def _create_columns_from_list_of_groups_of_marked_up_str_forced_order(
    list_of_groups_of_marked_up_str: ListOfGroupsOfMarkedUpStrings,
    report_options: ReportingOptionsForSpecificGroupsInReport,
) -> ListtOfColumns:
    force_order_list_of_indices = (
        report_options.arrange_groups.arrangement_of_columns
    )

    return _create_columns_from_list_of_groups_of_marked_up_str_with_passed_list(
        list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
        order_list_of_indices=force_order_list_of_indices,
    )


def _create_columns_from_list_of_groups_of_marked_up_str_optimise_size(
    list_of_groups_of_marked_up_str: ListOfGroupsOfMarkedUpStrings,
    report_options: ReportingOptionsForSpecificGroupsInReport,
) -> ListtOfColumns:

    ## want to get ratio as close as possible to h/w ratio which will come from paper size
    ## generate all possible combinations and test
    group_count = len(list_of_groups_of_marked_up_str)
    series_of_possible_indices = _generate_list_of_all_possible_indices(group_count)

    best_list_of_indices = _find_best_list_of_indices(
        series_of_possible_indices=series_of_possible_indices,
        list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
        report_options=report_options,
    )

    best_list_of_columns = (
        _create_columns_from_list_of_groups_of_marked_up_str_with_passed_list(
            list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
            order_list_of_indices=best_list_of_indices,
        )
    )

    return best_list_of_columns

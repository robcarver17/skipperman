from dataclasses import dataclass
from typing import List

from app.logic.reporting.backend.TODELETE import (
    ReportingOptionsForSpecificGroupsInReport,
)
from app.reporting.process_stages.strings_columns_groups import (
    ListOfGroupsOfMarkedUpStrings,
    create_columns_from_list_of_groups_of_marked_up_str_with_passed_list,
)


@dataclass()
class PossibleIndex:
    items_yet_to_be_allocated: list
    index: List[List[int]] = None

    def add_group_and_return_new_index(self, group: List[int]):
        remaining = remaining_from_passed_list_given_group(
            self.items_yet_to_be_allocated, group
        )
        if self.index is None:
            new_index = [group]
        else:
            new_index = self.index + [group]

        return PossibleIndex(items_yet_to_be_allocated=remaining, index=new_index)

    @property
    def finished(self):
        return len(self.items_yet_to_be_allocated) == 0


def _generate_list_of_all_possible_indices(group_count: int) -> List[List[List[int]]]:
    generate_list = list(range(group_count))
    starting_list = [PossibleIndex(items_yet_to_be_allocated=generate_list)]

    list_of_all_possible_indices_as_objects = generate_indices_given_passed_list(
        starting_list
    )

    list_of_possible_indices = [
        item.index for item in list_of_all_possible_indices_as_objects
    ]

    return list_of_possible_indices


def generate_indices_given_passed_list(
    list_of_possible_indices_so_far: List[PossibleIndex],
):
    finished = [
        existing_index
        for existing_index in list_of_possible_indices_so_far
        if existing_index.finished
    ]
    unfinished = [
        existing_index
        for existing_index in list_of_possible_indices_so_far
        if not existing_index.finished
    ]
    if len(unfinished) == 0:
        return list_of_possible_indices_so_far

    new_items_from_unfinished = []
    for unfinished_item in unfinished:
        items_yet_to_be_allocated = unfinished_item.items_yet_to_be_allocated
        possible_groups = [
            items_yet_to_be_allocated[: i + 1]
            for i in range(len(items_yet_to_be_allocated))
        ]
        list_of_new_items_for_this_unfinished = [
            unfinished_item.add_group_and_return_new_index(group)
            for group in possible_groups
        ]
        new_items_from_unfinished += list_of_new_items_for_this_unfinished

    new_list = finished + new_items_from_unfinished

    return generate_indices_given_passed_list(new_list)


def remaining_from_passed_list_given_group(passed_list: list, group: list):
    return list(set(passed_list).difference(group))


def _find_best_list_of_indices(
    series_of_possible_indices: List[List[List[int]]],
    list_of_groups_of_marked_up_str: ListOfGroupsOfMarkedUpStrings,
    report_options: ReportingOptionsForSpecificGroupsInReport,
) -> List[List[int]]:
    tracking_errors = [
        _tracking_error_for_list_of_indices(
            list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
            order_list_of_indices=order_list_of_indices,
            report_options=report_options,
        )
        for order_list_of_indices in series_of_possible_indices
    ]

    min_tracking_error = min(tracking_errors)
    index_min_tracking_error = tracking_errors.index(min_tracking_error)

    return series_of_possible_indices[index_min_tracking_error]


def _tracking_error_for_list_of_indices(
    order_list_of_indices: List[List[int]],
    list_of_groups_of_marked_up_str: ListOfGroupsOfMarkedUpStrings,
    report_options: ReportingOptionsForSpecificGroupsInReport,
) -> float:
    list_of_columns = (
        create_columns_from_list_of_groups_of_marked_up_str_with_passed_list(
            list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
            arrangement_of_columns=order_list_of_indices,
        )
    )

    equalise_columns = report_options.equalise_columns
    height_of_title_in_characters = report_options.height_of_title_in_characters
    optimal_ratio = report_options.print_options.ratio_of_width_to_height()

    actual_ratio = list_of_columns.ratio_of_required_width_to_height(
        equalise_columns=equalise_columns,
        height_of_title_in_characters=height_of_title_in_characters,
    )

    return abs(optimal_ratio - actual_ratio)

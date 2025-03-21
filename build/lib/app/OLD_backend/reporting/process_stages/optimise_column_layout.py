from app.backend.reporting import PrintOptions
from app.backend.reporting import ArrangementOfColumns
from dataclasses import dataclass
from typing import List

from app.backend.reporting import (
    Page,
    create_columns_from_page,
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


def _generate_list_of_all_possible_indices(
    group_count: int,
) -> List[ArrangementOfColumns]:
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
) -> ArrangementOfColumns:
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
        return ArrangementOfColumns(list_of_possible_indices_so_far)

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
    series_of_possible_indices: List[ArrangementOfColumns],
    page: Page,
    print_options: PrintOptions,
) -> ArrangementOfColumns:
    tracking_errors = [
        _tracking_error_for_list_of_indices(
            page=page,
            order_list_of_indices=order_list_of_indices,
            print_options=print_options,
        )
        for order_list_of_indices in series_of_possible_indices
    ]

    min_tracking_error = min(tracking_errors)
    index_min_tracking_error = tracking_errors.index(min_tracking_error)

    return series_of_possible_indices[index_min_tracking_error]


def _tracking_error_for_list_of_indices(
    order_list_of_indices: ArrangementOfColumns,
    page: Page,
    print_options: PrintOptions,
) -> float:
    list_of_columns = create_columns_from_page(
        page=page,
        arrangement_of_columns=order_list_of_indices,
    )

    equalise_columns = print_options.equalise_column_width
    height_of_title_in_characters = print_options.height_of_title_in_characters
    optimal_ratio = print_options.ratio_of_width_to_height()

    actual_ratio = list_of_columns.ratio_of_required_width_to_height(
        equalise_columns=equalise_columns,
        height_of_title_in_characters=height_of_title_in_characters,
    )

    tracking = abs(optimal_ratio - actual_ratio)
    print(tracking)
    return tracking

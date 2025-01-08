from copy import copy
from typing import Union, List
from dataclasses import dataclass

import pandas as pd

from app.backend.reporting.arrangement.group_order import GroupOrder
from app.frontend.reporting.shared.report_generator import ReportGenerator
from app.objects.exceptions import arg_not_passed
from app.backend.reporting.arrangement.arrangement_order import ArrangementOfColumns
from app.backend.reporting.arrangement.arrangement_methods import (
    ArrangementMethod,
    ARRANGE_PASSED_LIST,
    ARRANGE_RECTANGLE,
    DEFAULT_ARRANGEMENT,
    POSSIBLE_ARRANGEMENTS_NOT_PASSING,
)
from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_definitions import object_definition_for_report_arrangement_and_group_order_options

class ArrangeGroupsOptions:
    def __init__(
        self,
        arrangement_method: ArrangementMethod = DEFAULT_ARRANGEMENT,
        arrangement_of_columns: ArrangementOfColumns = arg_not_passed,
    ):
        if arrangement_of_columns is arg_not_passed:
            arrangement_of_columns = ArrangementOfColumns()

        self._arrangement_method = arrangement_method
        self._arrangement_of_columns = arrangement_of_columns

    def __repr__(self):
        return "%s: Indices %s" % (
            describe_arrangement(self.arrangement_method),
            str(self.arrangement_of_columns),
        )

    @classmethod
    def create_empty(cls):
        return cls()

    def no_arrangement_of_columns_provided(self) -> bool:
        return len(self.arrangement_of_columns) == 0

    def delete_arrangement_of_columns(self):
        self._arrangement_of_columns = ArrangementOfColumns()

    def add_arrangement_of_columns(
        self, new_arrangement_of_columns: ArrangementOfColumns
    ):
        self._arrangement_of_columns = new_arrangement_of_columns
        self._arrangement_method = ARRANGE_PASSED_LIST

    def change_arrangement_options_given_new_method_name(
        self, arrangment_method_name: str
    ):
        arrangement_method = dict_of_arrangements_that_reorder[arrangment_method_name]
        self.change_arrangement_options_given_new_method(arrangement_method)

    def change_arrangement_options_given_new_method(
        self, arrangement_method: ArrangementMethod
    ):
        self._arrangement_method = arrangement_method

        ## AS we are now using a specific method, delete custom arrangement
        self.delete_arrangement_of_columns()

    def reset_arrangement_back_to_default(self):
        self.change_arrangement_options_given_new_method(DEFAULT_ARRANGEMENT)

    def replace_column_arrangement(self, new_column_arrangement: ArrangementOfColumns):
        self._arrangement_of_columns = new_column_arrangement

    @property
    def arrangement_of_columns(self) -> ArrangementOfColumns:
        return self._arrangement_of_columns

    @property
    def arrangement_method(self) -> ArrangementMethod:
        return self._arrangement_method


@dataclass
class ArrangementOptionsAndGroupOrder:
    arrangement_options: ArrangeGroupsOptions
    group_order: GroupOrder

    @classmethod
    def create_empty(cls):
        return cls(
            arrangement_options=ArrangeGroupsOptions(), group_order=GroupOrder([])
        )

    def does_arrangement_include_all_groups(self) -> bool:
        all_group_indices_in_arrangement = (
            self.arrangement_options.arrangement_of_columns.items_in_self()
        )
        all_groups_as_count = list(range(len(self.group_order)))

        return all_group_indices_in_arrangement == all_groups_as_count

    def replace_column_arrangement(self, new_column_arrangement: ArrangementOfColumns):
        self.arrangement_options.replace_column_arrangement(new_column_arrangement)

    @classmethod
    def from_group_order_and_column_arrangements(
        cls, group_order: GroupOrder, arrangement_of_columns: ArrangementOfColumns
    ):
        return cls(
            group_order=group_order,
            arrangement_options=ArrangeGroupsOptions(
                arrangement_of_columns=arrangement_of_columns,
                arrangement_method=DEFAULT_ARRANGEMENT,
            ),
        )

    def is_empty(self):
        return len(self.group_order) == 0

    def reset_arrangement_back_to_default(self):
        self.arrangement_options.reset_arrangement_back_to_default()

    def remove_empty_groups_from_group_order_and_arrangement(
        self, empty_groups: GroupOrder
    ):
        new_group_list = self.group_order.me_but_with_other_groups_removed(empty_groups)

        self.subset_if_in_other_group_order(new_group_list)

    def add_missing_groups_to_group_order_and_arrangement(
        self,
        missing_groups: GroupOrder,
    ):
        current_group_order = self.group_order
        current_columns = (
            self.arrangement_options.arrangement_of_columns
        )  ###uses indices
        for group in missing_groups:
            if group not in current_group_order:
                current_group_order.append(group)
                index_of_group_in_group_order = current_group_order.index(
                    group
                )  ## should be a new one
                current_columns.insert_value_at_top_left(index_of_group_in_group_order)

        current_columns.remove_empty_elements()

    def subset_if_in_other_group_order(self, other_group_order: List):
        ## change both group order and arrangement options
        starting_group_order = copy(self.group_order)
        current_group_order = self.group_order
        current_columns = (
            self.arrangement_options.arrangement_of_columns
        )  ###uses indices
        for group in starting_group_order:
            if group not in other_group_order:
                index_of_group_in_group_order = current_group_order.index(group)

                current_columns.remove_value_and_reset_indices(
                    index_of_group_in_group_order
                )
                current_group_order.pop(index_of_group_in_group_order)

        current_columns.remove_empty_elements()

    def as_df_of_str(self) -> pd.DataFrame:
        method = self.arrangement_options.arrangement_method.name
        columns = self.arrangement_options.arrangement_of_columns.as_str()
        group_order = self.group_order.as_str()

        return pd.DataFrame(
            dict(method=[method], columns=[columns], group_order=[group_order])
        )

    @classmethod
    def from_df_of_str(cls, df: pd.DataFrame):
        method_str = df["method"].iloc[0]
        if pd.isna(method_str):
            method = DEFAULT_ARRANGEMENT
        else:
            method = ArrangementMethod[method_str]

        columns_str = df["columns"].iloc[0]
        if pd.isna(columns_str):
            columns = ArrangementOfColumns()
        else:
            columns = ArrangementOfColumns.from_str(columns_str)

        group_order_str = df["group_order"].iloc[0]
        if pd.isna(group_order_str):
            group_order = GroupOrder()
        else:
            group_order = GroupOrder.from_str(group_order_str)

        return cls(
            arrangement_options=ArrangeGroupsOptions(
                arrangement_method=method, arrangement_of_columns=columns
            ),
            group_order=group_order,
        )


def describe_arrangement(
    arrangement_options: Union[ArrangeGroupsOptions, ArrangementMethod]
) -> str:
    if type(arrangement_options) is not ArrangementMethod:
        arrangement = arrangement_options.arrangement_method
    else:
        arrangement = arrangement_options

    if arrangement == ARRANGE_PASSED_LIST:
        return "Arrange according to a user specified arrangement"

    elif arrangement == ARRANGE_RECTANGLE:
        return "Arrange in most efficient rectangle, assuming all groups same size"


dict_of_arrangements_that_reorder = dict(
    [
        (describe_arrangement(arrangement), arrangement)
        for arrangement in POSSIBLE_ARRANGEMENTS_NOT_PASSING
    ]
)


def get_stored_arrangement_and_group_order(
        object_store: ObjectStore, report_type: str
) -> ArrangementOptionsAndGroupOrder:
    return object_store.get(object_definition=object_definition_for_report_arrangement_and_group_order_options,
                            report_name=report_type)


def update_arrangement_and_group_order(
    object_store: ObjectStore,
    arrangement_and_group_options: ArrangementOptionsAndGroupOrder,
    report_type: str,
):
    object_store.update(
        object_definition=object_definition_for_report_arrangement_and_group_order_options,
        report_name=report_type,
        new_object=arrangement_and_group_options
    )


def reset_arrangement_report_options(
    object_store: ObjectStore, report_generator: ReportGenerator
):

    update_arrangement_and_group_order(
        object_store=object_store,
        report_type=report_generator.name,
        arrangement_and_group_options=ArrangementOptionsAndGroupOrder.create_empty()
    )

from enum import Enum
import pandas as pd
from dataclasses import dataclass
from typing import List

from data_access.configuration.configuration import (
    A4_PAGESIZE,
    UNIT_MM,
    TITLE_MULTIPLIER,
    PAGESIZE_MM,
    HEIGHT,
    WIDTH,
    EDGE_MARGIN_MM,
    COLUMN_GAP_MM,
)
from objects.constants import arg_not_passed


@dataclass
class PrintOptions:
    landscape: bool = True
    path_and_filename: str = ""
    title_str: str = ""
    equalise_column_width: bool = True
    page_size: str = A4_PAGESIZE
    font: str = "Arial"
    unit: str = UNIT_MM  ## DO NOT CHANGE OR ALL HELL WILL BREAK LOOSE

    @property
    def height_of_title_in_characters(self) -> int:
        title_str = self.title_str
        if len(title_str) == 0:
            return 0
        else:
            return TITLE_MULTIPLIER

    def ratio_of_width_to_height(self) -> float:
        return (
            self.page_width_measurement_units()
            / self.page_height_in_measurement_units()
        )

    def page_width_measurement_units(self) -> float:
        page_sizes_dict = self._page_sizes_dict()
        if self.landscape:
            return page_sizes_dict[HEIGHT]
        else:
            return page_sizes_dict[WIDTH]

    def page_height_in_measurement_units(self):
        page_sizes_dict = self._page_sizes_dict()
        if self.landscape:
            return page_sizes_dict[WIDTH]
        else:
            return page_sizes_dict[HEIGHT]

    def _page_sizes_dict(self) -> dict:
        page_size = self.page_size
        assert self.unit is UNIT_MM
        page_sizes_dict = PAGESIZE_MM[page_size]

        return page_sizes_dict

    @property
    def edge_margin_measurement_units(self):
        assert self.unit is UNIT_MM
        return EDGE_MARGIN_MM

    @property
    def column_gap_measurement_units(self) -> float:
        assert self.unit is UNIT_MM
        return COLUMN_GAP_MM

    @property
    def orientation(self) -> str:
        if self.landscape:
            orientation = "L"
        else:
            orientation = "P"

        return orientation


@dataclass
class MarkedUpListFromDfParameters:
    entry_columns: List[str]
    group_by_column: str
    passed_group_order: list
    include_group_as_header: bool = True
    first_value_in_group_is_key: bool = False
    prepend_group_name: bool = False


@dataclass
class MarkedUpListFromDfParametersWithActualGroupOrder:
    entry_columns: List[str]
    group_by_column: str
    actual_group_order: list
    include_group_as_header: bool = True
    first_value_in_group_is_key: bool = False
    prepend_group_name: bool = False

    @classmethod
    def from_marked_up_list_with_suggested_group_order(
        cls,
        marked_up_list_from_df_parameters: MarkedUpListFromDfParameters,
        actual_group_order,
    ):

        return cls(
            entry_columns=marked_up_list_from_df_parameters.entry_columns,
            group_by_column=marked_up_list_from_df_parameters.group_by_column,
            actual_group_order=actual_group_order,
            include_group_as_header=marked_up_list_from_df_parameters.include_group_as_header,
            first_value_in_group_is_key=marked_up_list_from_df_parameters.first_value_in_group_is_key,
            prepend_group_name=marked_up_list_from_df_parameters.prepend_group_name,
        )


ArrangementMethod = Enum("ArrangementMethod", ["Optimise", "PassedList", "Rectangle"])
ARRANGE_OPTIMISE = ArrangementMethod.Optimise
ARRANGE_PASSED_LIST = ArrangementMethod.PassedList
ARRANGE_RECTANGLE = ArrangementMethod.Rectangle
POSSIBLE_ARRANGEMENTS = [ARRANGE_RECTANGLE, ARRANGE_OPTIMISE, ARRANGE_PASSED_LIST]


def describe_arrangement(arrangement: ArrangementMethod) -> str:
    if arrangement is ARRANGE_PASSED_LIST:
        return "Arrange according to a user specified list"

    elif arrangement is ARRANGE_RECTANGLE:
        return "Arrange in most efficient rectangle, assuming all groups same size"

    elif arrangement is ARRANGE_OPTIMISE:
        return "Optimise for best use of space"


@dataclass
class ArrangeGroupsOptions:
    arrangement: ArrangementMethod = ARRANGE_OPTIMISE
    force_order_of_columns_list_of_indices: List[List[int]] = arg_not_passed


### Bring everything together
@dataclass
class ReportingOptions:
    arrange_groups: ArrangeGroupsOptions
    marked_up_list_from_df: MarkedUpListFromDfParameters
    print_options: PrintOptions


@dataclass
class ReportingOptionsForSpecificGroupsInReport(ReportingOptions):
    arrange_groups: ArrangeGroupsOptions
    marked_up_list_from_df: MarkedUpListFromDfParametersWithActualGroupOrder
    print_options: PrintOptions
    list_of_groups: list

    ## only need to include things that will be accessed from 'wrong' place
    @property
    def landscape(self):
        return self.print_options.landscape

    @property
    def equalise_columns(self) -> bool:
        return self.print_options.equalise_column_width

    @property
    def height_of_title_in_characters(self) -> int:
        return self.print_options.height_of_title_in_characters

    @property
    def actual_group_order(self) -> List[str]:
        return self.marked_up_list_from_df.actual_group_order

    def describe_arrange_groups(self) -> str:
        if self.arrange_groups.arrangement is ARRANGE_PASSED_LIST:
            list_of_indices = self.arrange_groups.force_order_of_columns_list_of_indices
            actual_group_order = self.actual_group_order
            list_of_indices_shown_with_group_names = 0
            return (
                "Arrange groups in the following columns %s"
                % list_of_indices_shown_with_group_names
            )
        else:
            return describe_arrangement(self.arrange_groups.arrangement)


def adjust_reporting_options_to_reflect_passed_dataframe(
    df: pd.DataFrame, reporting_options_before_adjustment: ReportingOptions
) -> ReportingOptionsForSpecificGroupsInReport:

    list_of_groups_in_df = get_list_of_natural_groups_from_df(
        df=df,
        marked_up_list_from_df_parameters=reporting_options_before_adjustment.marked_up_list_from_df,
    )

    marked_up_list_from_df_with_adjusted_groups = adjust_df_parameters_to_reflect_actual_groups(
        marked_up_list_from_df_parameters=reporting_options_before_adjustment.marked_up_list_from_df,
        list_of_groups_in_df=list_of_groups_in_df,
    )

    return ReportingOptionsForSpecificGroupsInReport(
        marked_up_list_from_df=marked_up_list_from_df_with_adjusted_groups,
        list_of_groups=list_of_groups_in_df,
        print_options=reporting_options_before_adjustment.print_options,
        arrange_groups=reporting_options_before_adjustment.arrange_groups,
    )


def get_list_of_natural_groups_from_df(
    df: pd.DataFrame,
    marked_up_list_from_df_parameters: MarkedUpListFromDfParameters,
) -> list:
    grouped_df = df.groupby(marked_up_list_from_df_parameters.group_by_column)
    list_of_groups = list(grouped_df.groups.keys())

    return list_of_groups


def adjust_df_parameters_to_reflect_actual_groups(
    marked_up_list_from_df_parameters: MarkedUpListFromDfParameters,
    list_of_groups_in_df: list,
) -> MarkedUpListFromDfParametersWithActualGroupOrder:

    ## retains order but only for elements present
    passed_order_of_groups_in_marked_up_list = (
        marked_up_list_from_df_parameters.passed_group_order
    )
    actual_group_order = [
        group
        for group in passed_order_of_groups_in_marked_up_list
        if group in list_of_groups_in_df
    ]

    marked_up_list_from_df_parameters_with_actual_group_order = MarkedUpListFromDfParametersWithActualGroupOrder.from_marked_up_list_with_suggested_group_order(
        actual_group_order=actual_group_order,
        marked_up_list_from_df_parameters=marked_up_list_from_df_parameters,
    )

    return marked_up_list_from_df_parameters_with_actual_group_order

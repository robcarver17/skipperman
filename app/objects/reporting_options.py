from dataclasses import dataclass
from enum import Enum
from typing import List

import pandas as pd

from app.data_access.configuration.configuration import A4_PAGESIZE, UNIT_MM, TITLE_MULTIPLIER, HEIGHT, WIDTH, \
    PAGESIZE_MM, EDGE_MARGIN_MM, COLUMN_GAP_MM
from app.objects.constants import arg_not_passed

from app.objects.generic import GenericSkipperManObject

@dataclass
class PrintOptions(GenericSkipperManObject):
    filename: str = ""
    title_str: str = ""
    page_size: str = A4_PAGESIZE
    font: str = "Arial"
    unit: str = UNIT_MM  ## DO NOT CHANGE OR ALL HELL WILL BREAK LOOSE
    include_group_as_header: bool = True
    first_value_in_group_is_key: bool = False
    prepend_group_name: bool = False
    equalise_column_width: bool = True
    landscape: bool = True

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


POSSIBLE_ARRANGEMENT_NAMES= ["Optimise", "PassedList", "Rectangle"]
ArrangementMethod = Enum("ArrangementMethod", POSSIBLE_ARRANGEMENT_NAMES)
ARRANGE_OPTIMISE = ArrangementMethod.Optimise
ARRANGE_PASSED_LIST = ArrangementMethod.PassedList
ARRANGE_RECTANGLE = ArrangementMethod.Rectangle
POSSIBLE_ARRANGEMENTS = [ARRANGE_RECTANGLE, ARRANGE_OPTIMISE, ARRANGE_PASSED_LIST]


DEFAULT_ARRANGEMENT_NAME = "Optimise"
DEFAULT_ARRANGEMENT = ArrangementMethod[DEFAULT_ARRANGEMENT_NAME]

from typing import Union
def describe_arrangement(arrangement_options: Union[ 'ArrangeGroupsOptions', ArrangementMethod]) -> str:
    if type(arrangement_options) is not ArrangementMethod:
        arrangement = arrangement_options.arrangement
    else:
        arrangement = arrangement_options

    if arrangement is ARRANGE_PASSED_LIST:
        return "Arrange according to a user specified arrangement"

    elif arrangement is ARRANGE_RECTANGLE:
        return "Arrange in most efficient rectangle, assuming all groups same size"

    elif arrangement is ARRANGE_OPTIMISE:
        return "Optimise for best use of space"


@dataclass
class ArrangeGroupsOptions:
    arrangement: ArrangementMethod = DEFAULT_ARRANGEMENT
    force_order_of_columns_list_of_indices: List[List[int]] = arg_not_passed

    @property
    def no_list_provided(self):
        return self.force_order_of_columns_list_of_indices is arg_not_passed
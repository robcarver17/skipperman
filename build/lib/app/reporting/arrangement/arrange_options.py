from typing import Union
from dataclasses import dataclass

from app.backend.reporting.arrangement.group_order import GroupOrder
from app.objects.constants import arg_not_passed
from app.backend.reporting.arrangement.arrangement_order import ArrangementOfColumns
from app.backend.reporting.arrangement.arrangement_methods import (
    ArrangementMethod,
    ARRANGE_PASSED_LIST,
    ARRANGE_RECTANGLE,
    ARRANGE_OPTIMISE,
    DEFAULT_ARRANGEMENT, POSSIBLE_ARRANGEMENTS_NOT_PASSING, )


def describe_arrangement(
    arrangement_options: Union["ArrangeGroupsOptions", ArrangementMethod]
) -> str:
    if type(arrangement_options) is not ArrangementMethod:
        arrangement = arrangement_options.arrangement_method
    else:
        arrangement = arrangement_options

    if arrangement == ARRANGE_PASSED_LIST:
        return "Arrange according to a user specified arrangement"

    elif arrangement == ARRANGE_RECTANGLE:
        return "Arrange in most efficient rectangle, assuming all groups same size"

    elif arrangement == ARRANGE_OPTIMISE:
        return "Optimise for best use of space"


class ArrangeGroupsOptions:
    def __init__(
        self,
        arrangement_method: ArrangementMethod = DEFAULT_ARRANGEMENT,
        arrangement_of_columns: ArrangementOfColumns = arg_not_passed
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

    def no_arrangement_of_columns_provided(self) ->bool:
        return len(self.arrangement_of_columns) == 0

    def delete_arrangement_of_columns(self):
        self._arrangement_of_columns = ArrangementOfColumns()

    def add_arrangement_of_columns(self, new_arrangement_of_columns: ArrangementOfColumns):
        self._arrangement_of_columns = new_arrangement_of_columns
        self._arrangement_method = ARRANGE_PASSED_LIST

    def change_arrangement_options_given_new_method_name(self, arrangment_method_name: str):
        arrangement_method = dict_of_arrangements_that_reorder[arrangment_method_name]
        self._arrangement_method = arrangement_method

        ## AS we are now using a specific method, delete custom arrangement
        self.delete_arrangement_of_columns()

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


dict_of_arrangements_that_reorder = dict(
    [
        (describe_arrangement(arrangement), arrangement)
        for arrangement in POSSIBLE_ARRANGEMENTS_NOT_PASSING
    ]
)

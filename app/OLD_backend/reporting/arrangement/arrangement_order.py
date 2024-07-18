from copy import copy
from dataclasses import dataclass
from typing import List

import numpy as np

from app.objects.utils import in_x_not_in_y

MARK_AS_DELETE = -9999


@dataclass
class IndicesToSwap:
    idx1: int
    idx2: int

    @classmethod
    def create_delete_index(cls, idx):
        return cls(MARK_AS_DELETE, idx)

    @property
    def is_delete_index(self):
        return self.idx1 == MARK_AS_DELETE

    def index_to_delete(self):
        assert self.is_delete_index
        return self.idx2


class GenericArrangement(list):
    @classmethod
    def from_str(cls, the_string: str):
        return cls(eval(the_string))

    def as_str(self):
        return str(self)

    def remove_empty_elements(self):
        while True:
            empty = [i for i in range(len(self)) if len(self[i]) == 0]
            if len(empty) == 0:
                return
            self.pop(empty[0])

    def as_matrix(self) -> np.matrix:
        arrangement = copy(self)
        return np.matrix(arrangement)

    @classmethod
    def from_matrix(cls, matrix: np.matrix):
        return cls(matrix.tolist())


class ArrangementOfRows(GenericArrangement):
    def transpose_to_columns(self) -> "ArrangementOfColumns":
        return ArrangementOfColumns.from_matrix(self.as_matrix().transpose())


@dataclass
class Position:
    column: int
    row: int


EMPTY = -1


class ArrangementOfColumns(GenericArrangement):
    def add_extra_items_from_other_arrangement(
        self, other_arrangement: "ArrangementOfColumns"
    ):
        items_in_self = self.items_in_self()
        items_in_other = other_arrangement.items_in_self()

        new_items = in_x_not_in_y(x=items_in_other, y=items_in_self)

        for item in new_items:
            self.insert_value_at_bottom_right(item)

    def swap_or_delete_indices(self, indices_to_swap: IndicesToSwap):
        if indices_to_swap.is_delete_index:
            return self.delete_value_given_indices(indices_to_swap)
        else:
            return self.swap_indices(indices_to_swap)

    def swap_indices(self, indices_to_swap: IndicesToSwap):
        idx1 = indices_to_swap.idx1
        idx2 = indices_to_swap.idx2

        new_version = copy(self)
        for i in range(len(self)):
            for j in range(len(self[i])):
                old = self[i][j]
                if old == idx1:
                    new_version[i][j] = idx2
                if old == idx2:
                    new_version[i][j] = idx1
        return new_version

    def delete_value_given_indices(self, indices_to_swap: IndicesToSwap):
        value_to_delete = indices_to_swap.index_to_delete()
        self.remove_value_and_reset_indices(value_to_delete)
        return self

    def remove_value_and_reset_indices(self, value):
        try:
            self.remove_value(value)
        except IndexError:
            ## already missing nothing to do
            pass

        ## Always need to do this though
        self.reset_indices(value)

    def remove_value(self, value):
        current_position = self.position_of_value(value)
        self.remove_value_from_current_column(current_position)

    def reset_indices(self, value):
        for i in range(len(self)):
            column = self[i]
            for j in range(len(column)):
                cell = self[i][j]
                if cell < value:
                    continue
                ## can't be equal so must be higher
                cell = cell - 1
                self[i][j] = cell

    def left(self, value):
        current_index = self.position_of_value(value)
        if current_index.column == 0:
            new_column = [value]
            self.remove_value_from_current_column(current_index)
            self.insert(0, new_column)
        else:
            self.insert_value_in_new_column(
                value, current_index.column - 1, current_index.row
            )
            self.remove_value_from_current_column(current_index)

    def right(self, value):
        current_index = self.position_of_value(value)
        if current_index.column == self.max_column_index:
            new_column = [value]
            self.remove_value_from_current_column(current_index)
            self.insert(len(self) + 1, new_column)
        else:
            self.insert_value_in_new_column(
                value, current_index.column + 1, current_index.row
            )
            self.remove_value_from_current_column(current_index)

    def up(self, value):
        current_index = self.position_of_value(value)
        if current_index.row == 0:
            pass
        else:
            self.swap_two_values_in_column(
                current_index.column, current_index.row, current_index.row - 1
            )

    def down(self, value):
        current_index = self.position_of_value(value)
        if current_index.row == self.max_row_index(current_index.column):
            pass
        else:
            self.swap_two_values_in_column(
                current_index.column, current_index.row + 1, current_index.row
            )

    def remove_value_from_current_column(self, position: Position):
        current_column = self[position.column]
        current_column.pop(position.row)
        if len(current_column) == 0:
            self.pop(position.column)

    def insert_value_at_top_left(self, value):
        if len(self) == 0:
            self.insert(0, [value])
            return

        self.insert_value_in_new_column(value, 0, 0)

    def insert_value_at_bottom_right(self, value):
        if len(self) == 0:
            self.insert(0, [value])
            return

        last_column_idx = -1
        last_column_length = len(self[last_column_idx])
        self.insert_value_in_new_column(value, last_column_idx, last_column_length)

    def insert_value_in_new_column(self, value, new_column_idx, row_idx):
        current_column = self[new_column_idx]
        current_column.insert(row_idx, value)

    def swap_two_values_in_column(self, column_idx, row_idx1, row_idx2):
        value1 = copy(self[column_idx][row_idx1])
        value2 = copy(self[column_idx][row_idx2])
        self[column_idx][row_idx2] = value1
        self[column_idx][row_idx1] = value2

    def position_of_value(self, value) -> Position:
        relevant_column_number = [
            column_number
            for column_number, column in enumerate(self)
            if value in column
        ][0]
        relevant_row = self[relevant_column_number].index(value)

        return Position(relevant_column_number, relevant_row)

    def transpose_to_rows(self) -> ArrangementOfRows:
        padded = pad_columns_to_square(self)
        return ArrangementOfRows.from_matrix(padded.as_matrix().transpose())

    def items_in_self(self):
        all_items = []
        for column in self:
            all_items += column

        return list(set(all_items))

    @property
    def max_column_index(self):
        return len(self) - 1

    def max_row_index(self, columnidx):
        return len(self[columnidx]) - 1


def pad_columns_to_square(arrangement: ArrangementOfColumns):
    max_column_length = max(len(column) for column in arrangement)
    new_arrangement = []
    for column in arrangement:
        add_items = [EMPTY] * (max_column_length - len(column))
        new_arrangement.append(column + add_items)

    return ArrangementOfColumns(new_arrangement)

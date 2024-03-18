from copy import copy
from dataclasses import dataclass
from typing import List

import numpy as np


class GenericArrangement(list):
    def as_matrix(self) -> np.matrix:
        arrangement = copy(self)
        return np.matrix(self)

    @classmethod
    def from_matrix(cls, matrix: np.matrix):
        return cls(matrix.tolist())

    def swap_indices(self, indices: tuple):
        idx1, idx2 = indices
        new_version = copy(self)
        for i in range(len(self)):
            for j in range(len(self[i])):
                old = self[i][j]
                if old == idx1:
                    new_version[i][j] = idx2
                if old == idx2:
                    new_version[i][j] = idx1
        return new_version


class ArrangementOfRows(GenericArrangement):
    def transpose_to_columns(self) -> "ArrangementOfColumns":
        return ArrangementOfColumns.from_matrix(self.as_matrix().transpose())


@dataclass
class Position:
    column: int
    row: int


EMPTY = -1


class ArrangementOfColumns(GenericArrangement):
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

class ListOfArrangementOfColumns(List[ArrangementOfColumns]):
    pass
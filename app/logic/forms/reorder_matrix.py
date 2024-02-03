from app.objects.abstract_objects.abstract_tables import RowInTable, Table
from app.objects.abstract_objects.abstract_text import up_arrow, down_arrow, \
    right_arrow, left_arrow
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line
from app.backend.reporting.arrangement.arrangement_order import (
    ArrangementOfRows,
    EMPTY,
    ArrangementOfColumns,
)



def reorder_matrix(
    current_list_of_entries: list,
    arrangement_of_rows: ArrangementOfRows,
) -> Table:

    rows = []
    for row_index, current_order_as_list_for_row in enumerate(arrangement_of_rows):
        row = reorder_matrix_table_row(
            current_list_of_entries=current_list_of_entries,
            row_index=row_index,
            current_order_as_list_for_row=current_order_as_list_for_row,
        )
        rows.append(row)

    return Table(rows, has_column_headings=False, has_row_headings=False)


def reorder_matrix_table_row(
    current_list_of_entries: list, current_order_as_list_for_row: list, row_index: int
) -> RowInTable:
    row_elements = []
    for column_index, index_in_list in enumerate(current_order_as_list_for_row):
        element = reorder_matrix_table_element(
            current_list_of_entries=current_list_of_entries,
            row_index=row_index,
            index_in_list=index_in_list,
        )
        row_elements.append(element)
        # row_elements.append(" ")

    return RowInTable(row_elements)


def reorder_matrix_table_element(
    current_list_of_entries: list, row_index: int, index_in_list: int
) -> Line:
    if index_in_list == EMPTY:
        return Line("")

    element_in_list = current_list_of_entries[index_in_list]
    up_button = Button(up_arrow, value=get_button_name(element_in_list, UP))
    down_button = Button(down_arrow, value=get_button_name(element_in_list, DOWN))
    left_button = Button(left_arrow, value=get_button_name(element_in_list, LEFT))
    right_button = Button(right_arrow, value=get_button_name(element_in_list, RIGHT))

    return Line([left_button, up_button, element_in_list, down_button, right_button])


UP = "UP"
DOWN = "DOWN"
LEFT = "LEFT"
RIGHT = "RIGHT"
DIVIDER = "_"  ##

def list_of_button_values_given_list_of_entries(list_of_entries: list) -> list:
    up_buttons = [get_button_name(entry, UP) for entry in list_of_entries]
    down_buttons = [get_button_name(entry, DOWN) for entry in list_of_entries]
    right_buttons = [get_button_name(entry, RIGHT) for entry in list_of_entries]
    left_buttons = [get_button_name(entry, LEFT) for entry in list_of_entries]

    return up_buttons+down_buttons+right_buttons+left_buttons

from app.logic.abstract_interface import abstractInterface


class reorderMatrixInterface:
    def __init__(
        self,
        interface: abstractInterface,
        current_arrangement_of_columns: ArrangementOfColumns,
        current_list_of_entries: list,
    ):
        self.interface = interface
        self.current_arrangement_of_columns = current_arrangement_of_columns
        self.current_list_of_entries = current_list_of_entries

    def new_arrangement(self) -> ArrangementOfColumns:
        last_button_pressed = self.interface.last_button_pressed()
        return modify_arrangement_given_button_name(
            button_name=last_button_pressed,
            current_arrangement_of_columns=self.current_arrangement_of_columns,
            current_list_of_entries=self.current_list_of_entries,
        )


def modify_arrangement_given_button_name(
    current_arrangement_of_columns: ArrangementOfColumns,
    button_name: str,
    current_list_of_entries: list,
) -> ArrangementOfColumns:
    element_name, action = from_button_name_to_action(button_name)
    index = current_list_of_entries.index(element_name)

    if action == UP:
        current_arrangement_of_columns.up(index)
    elif action == DOWN:
        current_arrangement_of_columns.down(index)
    elif action == RIGHT:
        current_arrangement_of_columns.right(index)
    elif action == LEFT:
        current_arrangement_of_columns.left(index)
    else:
        raise Exception("Button action not recoginsed")

    return current_arrangement_of_columns


def from_button_name_to_action(button_name: str):
    split_it = button_name.split(DIVIDER)

    return split_it[0], split_it[1]


def get_button_name(label, direction):
    return "%s%s%s" % (label, DIVIDER, direction)

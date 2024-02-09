from typing import Tuple
from copy import copy

from app.objects.abstract_objects.abstract_tables import RowInTable, Table
from app.objects.abstract_objects.abstract_text import up_arrow, down_arrow
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_interface import abstractInterface


class reorderFormInterface:
    def __init__(self, interface: abstractInterface, current_order: list):
        self.interface = interface
        self.current_order = current_order

    def indices_to_swap(self):
        last_button_pressed = self.interface.last_button_pressed()
        return indices_to_swap_given_button_name(
            current_order=self.current_order, button_name=last_button_pressed
        )

    def new_order_of_list(self):
        last_button_pressed = self.interface.last_button_pressed()
        return modify_list_given_button_name(
            current_order=self.current_order, button_name=last_button_pressed
        )


def list_of_button_names_given_group_order(current_order:list) -> list:
    up_buttons = [get_button_name(label, UP) for label in current_order]
    down_buttons = [get_button_name(label,DOWN) for label in current_order]

    return up_buttons+down_buttons

def modify_list_given_button_name(current_order: list, button_name: str) -> list:
    index, other_index = indices_to_swap_given_button_name(
        current_order=current_order, button_name=button_name
    )

    current_elmement = copy(current_order[index])
    other_element = copy(current_order[other_index])

    current_order[other_index] = current_elmement
    current_order[index] = other_element

    return current_order


def indices_to_swap_given_button_name(
    current_order: list, button_name: str
) -> Tuple[int, int]:
    element_name, action = from_button_name_to_action(button_name)
    index = current_order.index(element_name)
    last_item = index == (len(current_order) - 1)

    if (index == 0 and action == UP) or (last_item and action == DOWN):
        return 0, -1

    if action == UP:
        return index, index - 1
    elif action == DOWN:
        return index, index + 1
    else:
        raise Exception("Can't do this")


def from_button_name_to_action(button_name: str):
    split_it = button_name.split(DIVIDER)

    return split_it[0], split_it[1]



def reorder_table(
    starting_list: list,
) -> Table:

    reorder_table = Table(
        [
            row_in_reorder_form(
                element_in_list=element_in_list,
                list_index=list_index,
                starting_list=starting_list,
            )
            for list_index, element_in_list in enumerate(starting_list)
        ]
    )
    return reorder_table


UP = "UP"
DOWN = "DOWN"
DIVIDER = "_"  ##


def row_in_reorder_form(
    element_in_list: str, list_index: int, starting_list: list
) -> RowInTable:
    up_button = Button(up_arrow, value=get_button_name(element_in_list, UP))
    down_button = Button(down_arrow, value=get_button_name(element_in_list, DOWN))

    if list_index == 0:
        return RowInTable([element_in_list, down_button])
    if list_index == len(starting_list) - 1:
        return RowInTable([element_in_list, up_button])
    else:
        return RowInTable([element_in_list, up_button, down_button])


def get_button_name(label, direction):
    return "%s%s%s" % (label, DIVIDER, direction)

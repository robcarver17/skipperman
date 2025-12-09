from copy import copy
from dataclasses import dataclass

from app.backend.reporting.arrangement.arrangement_order import IndicesToSwap
from app.frontend.shared.buttons import (
    get_button_value_given_type_and_attributes,
    is_button_of_type,
    get_attributes_from_button_pressed_of_known_type,
)
from app.objects.abstract_objects.abstract_tables import RowInTable, Table
from app.objects.abstract_objects.abstract_text import up_arrow, down_arrow
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_interface import abstractInterface


class reorderFormInterface:
    def __init__(self, interface: abstractInterface, current_order: list):
        self.interface = interface
        self.current_order = current_order

    def indices_to_swap(self) -> IndicesToSwap:
        last_button_pressed = self.interface.last_button_pressed()
        return indices_to_swap_given_button_name(
            current_order=self.current_order, button_name=last_button_pressed
        )

    def new_order_of_list(self):
        last_button_pressed = self.interface.last_button_pressed()
        return modify_list_given_button_name(
            current_order=self.current_order, button_name=last_button_pressed
        )


def DEPRECATE_list_of_button_names_given_group_order(current_order: list) -> list:
    up_buttons = [get_button_name_to_move_in_list(label, UP) for label in current_order]
    down_buttons = [
        get_button_name_to_move_in_list(label, DOWN) for label in current_order
    ]
    delete_buttons = [
        get_button_name_to_move_in_list(label, DELETE) for label in current_order
    ]

    return up_buttons + down_buttons + delete_buttons


def modify_list_given_button_name(current_order: list, button_name: str) -> list:
    indices_to_swap = indices_to_swap_given_button_name(
        current_order=current_order, button_name=button_name
    )

    if indices_to_swap.is_delete_index:
        return modify_list_if_deleting(
            current_order=current_order, indices_to_swap=indices_to_swap
        )
    else:
        return modify_list_if_swapping(
            current_order=current_order, indices_to_swap=indices_to_swap
        )


def modify_list_if_swapping(
    current_order: list, indices_to_swap: IndicesToSwap
) -> list:
    new_order = copy(current_order)

    index = indices_to_swap.idx1
    other_index = indices_to_swap.idx2

    current_elmement = copy(current_order[index])
    other_element = copy(current_order[other_index])

    new_order[other_index] = current_elmement
    new_order[index] = other_element

    return new_order


def modify_list_if_deleting(
    current_order: list, indices_to_swap: IndicesToSwap
) -> list:
    new_order = copy(current_order)

    index = indices_to_swap.index_to_delete()
    new_order.pop(index)

    return new_order


def indices_to_swap_given_button_name(
    current_order: list, button_name: str
) -> IndicesToSwap:
    action_and_element = from_button_name_to_direction_and_element_name(button_name)
    element_name = action_and_element.element_name
    action = action_and_element.direction_or_action

    index = current_order.index(element_name)
    last_item = index == (len(current_order) - 1)

    if (index == 0 and action == UP) or (last_item and action == DOWN):
        return IndicesToSwap(0, -1)

    if action == UP:
        return IndicesToSwap(index, index - 1)
    elif action == DOWN:
        return IndicesToSwap(index, index + 1)
    elif action == DELETE:
        return IndicesToSwap.create_delete_index(index)
    else:
        raise Exception("Can't do this")


def reorder_table(starting_list: list, include_delete: bool = False) -> Table:
    reorder_table = Table(
        [
            row_in_reorder_form(
                element_in_list=element_in_list,
                list_index=list_index,
                starting_list=starting_list,
                include_delete=include_delete,
            )
            for list_index, element_in_list in enumerate(starting_list)
        ]
    )
    return reorder_table


UP = "UP"
DOWN = "DOWN"
DIVIDER = "_"  ##
DELETE = "Delete"


def row_in_reorder_form(
    element_in_list: str,
    list_index: int,
    starting_list: list,
    include_delete: bool = False,
) -> RowInTable:
    up_button = Button(
        up_arrow, value=get_button_name_to_move_in_list(element_in_list, UP)
    )
    down_button = Button(
        down_arrow, value=get_button_name_to_move_in_list(element_in_list, DOWN)
    )

    if list_index == 0:
        row = [element_in_list, down_button, ""]
    elif list_index == len(starting_list) - 1:
        row = [element_in_list, up_button, ""]
    else:
        row = [element_in_list, up_button, down_button]

    if include_delete:
        delete_button = Button(
            DELETE, value=get_button_name_to_move_in_list(element_in_list, DELETE)
        )
        row.append(delete_button)

    return RowInTable(row)


arrow_button_type = "arrowButton"


def is_button_arrow_button(value_of_button_pressed: str):
    return is_button_of_type(
        type_to_check=arrow_button_type, value_of_button_pressed=value_of_button_pressed
    )


@dataclass
class DirectionAndElement:
    direction_or_action: str
    element_name: str


def get_button_name_to_move_in_list(element: str, direction):
    return get_button_value_given_type_and_attributes(
        arrow_button_type, direction, element
    )


def from_button_name_to_direction_and_element_name(button_name: str):
    attributes = get_attributes_from_button_pressed_of_known_type(
        value_of_button_pressed=button_name, type_to_check=arrow_button_type
    )

    return DirectionAndElement(
        direction_or_action=attributes[0], element_name=attributes[1]
    )

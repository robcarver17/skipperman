from copy import copy

from app.logic.forms_and_interfaces.abstract_form import FINISHED_BUTTON_LABEL, ListOfLines, bold, \
    _______________, Button, Line, up_arrow, down_arrow
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface


class reorderFormInterface:
    def __init__(self, interface: abstractInterface, current_order: list):
        self.interface = interface
        self.current_order = current_order

    def new_order_of_list(self):
        last_button_pressed = self.interface.last_button_pressed()
        return modify_list_given_button_name(
            current_order=self.current_order,
            button_name=last_button_pressed
        )

    def finished(self):
        last_button =  self.interface.last_button_pressed()
        return last_button==FINISHED_BUTTON_NAME



def modify_list_given_button_name(current_order: list, button_name: str) -> list:
    element_name, action = from_button_name_to_action(button_name)
    index = current_order.index(element_name)
    last_item = index == (len(current_order)-1)

    if (index==0 and action==UP) or (last_item and action == DOWN):
        print("Can't push up top in list - swapping")
        first_element = copy(current_order[0])
        last_element = copy(current_order[-1])

        current_order[0] = last_element
        current_order[-1] = first_element

    current_elmement = copy(current_order[index])

    if action==UP:
        previous_element = copy(current_order[index-1])

        current_order[index] = previous_element
        current_order[index-1] = current_elmement
    elif action == DOWN:
        next_element = copy(current_order[index+1])

        current_order[index] = next_element
        current_order[index +1] = current_elmement
    else:
        raise Exception("Can't do this")

    return current_order

def from_button_name_to_action(button_name: str):
    split_it = button_name.split(DIVIDER)

    return split_it[0],split_it[1]


FINISHED_BUTTON_NAME = "finished_button"

def reorder_form(
    heading: str,
    starting_list: list,
    finished_button_label: str = FINISHED_BUTTON_LABEL) -> ListOfLines:

    return \
        ListOfLines([bold(heading), _______________]+
            [
                row_in_reorder_form(element_in_list=element_in_list, list_index=list_index, starting_list=starting_list) for list_index, element_in_list in enumerate(starting_list)
            ]
                    +[_______________, Button(finished_button_label, value=FINISHED_BUTTON_NAME)]
        )



UP = "UP"
DOWN="DOWN"
DIVIDER = "_" ##


def row_in_reorder_form(element_in_list: str, list_index: int, starting_list: list)-> Line:
    up_button = Button(up_arrow, value=get_button_name(element_in_list, UP))
    down_button = Button(down_arrow, value=get_button_name(element_in_list, DOWN))

    if list_index==0:
        return Line([element_in_list, down_button])
    if list_index==len(starting_list)-1:
        return Line([element_in_list, up_button])
    else:
        return Line([element_in_list, up_button, down_button])


def get_button_name(label, direction):
    return "%s%s%s" % (label, DIVIDER, direction)

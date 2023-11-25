from typing import Callable

import pandas as pd

from app.objects.field_list import FIELDS_WITH_DATES,  FIELDS_WITH_INTEGERS, SPECIAL_FIELDS
from typing import Union
import datetime
from dataclasses import dataclass
from app.objects.constants import arg_not_passed

MAIN_MENU_BUTTON_LABEL = "Main menu"
CANCEL_BUTTON_LABEL = "Cancel"
FINISHED_BUTTON_LABEL = "Finished"
BACK_BUTTON_LABEL = "Back"

def button_label_requires_going_back(button_label: str) -> bool:
    return button_label in [CANCEL_BUTTON_LABEL, FINISHED_BUTTON_LABEL, BACK_BUTTON_LABEL]

@dataclass
class Button:
    label: str

finished_button = Button(FINISHED_BUTTON_LABEL)
cancel_button = Button(CANCEL_BUTTON_LABEL)
back_button = Button(BACK_BUTTON_LABEL)

main_menu_button = Button(MAIN_MENU_BUTTON_LABEL)


@dataclass
class Input:
    input_label: str
    input_name: str

class Line(list):
    def __init__(self, passed_list: Union[list, Button, str, Input]):
        if type(passed_list) is not list:
            super().__init__([passed_list])
        else:
            super().__init__(passed_list)

    def __repr__(self):
        return "Line: contents %s" % super().__repr__()


class ListOfLines(list):
    def __repr__(self):
        return "ListOfLines: contents %s" % super().__repr__()

class Table(pd.DataFrame):
    pass

### FIX ME ADD 'GO BACK AND RETURN' FORM ATTRIBUTE, INCLUDE FUNCTION TO WRITE THIS WITH A SINGLE BUTTON
class Form(list):
    def __repr__(self):
        return "Form: contents %s" % super().__repr__()

def form_with_message_and_finished_button(message: str) -> Form:
    return Form(ListOfLines([
                Line(message),
                Line(finished_button)
                ]
        )
    )

def form_with_message(message: str) -> Form:
    return Form(ListOfLines([
                Line(message)
                ]
        )
    )

_______________ = Line("")

@dataclass
class textInput(Input):

    input_label: str
    input_name: str
    value: str = arg_not_passed


@dataclass
class dateInput(Input):
    input_label: str
    input_name: str
    value: datetime.date = arg_not_passed,

DEFAULT_LABEL = "__!_!__canbeanythingunlikely to be used"

@dataclass
class radioInput(Input):
    input_label: str
    input_name: str
    dict_of_options: dict
    default_label: str = arg_not_passed


@dataclass
class intInput(Input):
    input_label: str
    input_name: str
    value: int = arg_not_passed

@dataclass
class fileInput(Input):
    input_name: str = "file"
    accept: str = arg_not_passed
    # accept can be eg '.doc' or '.doc, .csv'



@dataclass
class NewForm:
    form_name: str



def construct_form_field_given_field_name(field_name: str,
                                               *args,
                                               **kwargs):

    form_function  = get_required_form_field_type(field_name)

    return form_function(*args, **kwargs)

def get_required_form_field_type(field_name: str)->Callable:
    if field_name in FIELDS_WITH_INTEGERS:
        return intInput
    elif field_name in FIELDS_WITH_DATES:
        return dateInput
    elif field_name in SPECIAL_FIELDS:
        raise Exception("Can't construct a form field for field name %s" % field_name)
    else:
        return textInput
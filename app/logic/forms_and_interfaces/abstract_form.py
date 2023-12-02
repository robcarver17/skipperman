from enum import Enum
from typing import Callable, List
import pandas as pd

from app.objects.field_list import (
    FIELDS_WITH_DATES,
    FIELDS_WITH_INTEGERS,
    SPECIAL_FIELDS,
)
from app.objects.field_list import (
    FIELDS_WITH_DATES,
    FIELDS_WITH_INTEGERS,
    SPECIAL_FIELDS,
)
from app.objects.field_list import (
    FIELDS_WITH_DATES,
    FIELDS_WITH_INTEGERS,
    SPECIAL_FIELDS,
)
from app.objects.field_list import (
    FIELDS_WITH_DATES,
    FIELDS_WITH_INTEGERS,
    SPECIAL_FIELDS,
)
from typing import Union
import datetime
from dataclasses import dataclass
from app.objects.constants import arg_not_passed

MAIN_MENU_BUTTON_LABEL = "Main menu"
CANCEL_BUTTON_LABEL = "Cancel"
FINISHED_BUTTON_LABEL = "Finished"
BACK_BUTTON_LABEL = "Back"


def button_label_requires_going_back(button_label: str) -> bool:
    return button_label in [CANCEL_BUTTON_LABEL, FINISHED_BUTTON_LABEL]


@dataclass
class Text:
    text: str
    bold: bool = False
    emphasis: bool = False


def bold(text):
    return Text(text, bold=True)


def emphasis(text):
    return Text(text, emphasis=True)


@dataclass
class Button:
    label: str
    name: str = arg_not_passed
    value: str = arg_not_passed


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

    def __add__(self, other):
        return ListOfLines(self + other)


class PandasDFTable(pd.DataFrame):
    pass


@dataclass
class ElementsInTable:
    contents: Union[Line, Button, str, float]
    heading: bool = False


class RowInTable(list):
    def __init__(
        self, contents, has_column_headings: bool = False, is_heading_row: bool = False
    ):
        super().__init__(contents)
        self.has_column_headings = has_column_headings
        self.is_heading_row = is_heading_row

    def __repr__(self):
        return "Row: contents %s\n" % super().__repr__()

    def get_elements(self) -> List[ElementsInTable]:
        elements = []
        for idx, element in enumerate(self):
            is_heading = (idx == 0 and self.has_column_headings) or self.is_heading_row
            element = ElementsInTable(element, heading=is_heading)
            elements.append(element)

        return elements


class Table(list):
    def __init__(
        self,
        contents: list,
        has_column_headings: bool = False,
        has_row_headings: bool = False,
    ):
        super().__init__(contents)
        self.has_column_headings = has_column_headings
        self.has_row_headings = has_row_headings

    def __repr__(self):
        return "Table: contents %s\n" % super().__repr__()

    def get_rows(self) -> List[RowInTable]:
        rows = []
        for idx, row in enumerate(self):
            is_heading_row = idx == 0 and self.has_row_headings
            rows.append(
                RowInTable(
                    row,
                    has_column_headings=self.has_column_headings,
                    is_heading_row=is_heading_row,
                )
            )

        return rows


### FIX ME ADD 'GO BACK AND RETURN' FORM ATTRIBUTE, INCLUDE FUNCTION TO WRITE THIS WITH A SINGLE BUTTON
class Form(list):
    def __repr__(self):
        return "Form: contents %s" % super().__repr__()


def form_with_message(message: str) -> Form:
    return Form(ListOfLines([Line(message)]))


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
    value: datetime.date = (arg_not_passed,)


DEFAULT_LABEL = "__!_!__canbeanythingunlikely to be used"


@dataclass
class radioInput(Input):
    input_label: str
    input_name: str
    dict_of_options: dict
    default_label: str = arg_not_passed


YES = "Yes"
NO = "No"


def yes_no_radio(input_label, input_name, default_is_yes: bool = True) -> radioInput:
    dict_of_options = dict(Yes=YES, No=NO)
    if default_is_yes:
        default_label = YES
    else:
        default_label = NO

    return radioInput(
        input_label=input_label,
        input_name=input_name,
        dict_of_options=dict_of_options,
        default_label=default_label,
    )


@dataclass
class dropDownInput(Input):
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


def construct_form_field_given_field_name(field_name: str, *args, **kwargs):
    form_function = get_required_form_field_type(field_name)

    return form_function(*args, **kwargs)


def get_required_form_field_type(field_name: str) -> Callable:
    if field_name in FIELDS_WITH_INTEGERS:
        return intInput
    elif field_name in FIELDS_WITH_DATES:
        return dateInput
    elif field_name in SPECIAL_FIELDS:
        raise Exception("Can't construct a form field for field name %s" % field_name)
    else:
        return textInput


@dataclass
class File:
    path_and_filename: str


Arrow = Enum("Arrow", ["Up", "Down", "Left", "Right"])
up_arrow = Arrow.Up
down_arrow = Arrow.Down
right_arrow = Arrow.Right
left_arrow = Arrow.Left

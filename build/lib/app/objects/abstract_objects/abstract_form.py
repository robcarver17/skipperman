import datetime
from typing import Callable

from app.objects.abstract_objects.abstract_text import Input
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.objects.field_list import (
    FIELDS_WITH_DATES,
    FIELDS_WITH_INTEGERS,
    SPECIAL_FIELDS,
)
from dataclasses import dataclass
from app.objects.constants import arg_not_passed


class Form(list):
    def __repr__(self):
        return "Form: contents %s" % super().__repr__()



@dataclass
class NewForm:
    form_name: str


def form_with_message(message: str) -> Form:
    return Form(ListOfLines([Line(message)]))


@dataclass
class radioInput(Input):
    input_label: str
    input_name: str
    dict_of_options: dict
    default_label: str = arg_not_passed


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
class checkboxInput(Input):
    dict_of_labels: dict
    dict_of_checked: dict
    input_name: str
    input_label: str




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
YES = "Yes"
NO = "No"

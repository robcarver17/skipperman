import datetime
from typing import Tuple

from app.objects.abstract_objects.abstract_text import Input
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from dataclasses import dataclass
from app.objects.utilities.exceptions import arg_not_passed


class Form(list):
    def __repr__(self):
        return "Form: contents %s" % super().__repr__()

    @property
    def title(self) -> str:
        return getattr(self, "_title", "")

    @title.setter
    def title(self, new_title: str):
        setattr(self, "_title", new_title)


@dataclass
class Link:
    string: str
    url: str
    open_new_window: bool = False


@dataclass
class HelpLink:
    text: str
    help_page_name: str


@dataclass
class Image:
    filename: str
    px_height_width: Tuple[int, int] = arg_not_passed
    ratio_size: int = arg_not_passed
    image_directory: str = arg_not_passed

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
    include_line_break: bool = True


@dataclass
class listInput(Input):
    input_label: str
    input_name: str
    list_of_options: list
    list_name: str = arg_not_passed
    default_option: str = ""


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
    line_break: bool = False


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
class File:
    path_and_filename: str


@dataclass
class textInput(Input):
    input_label: str
    input_name: str
    value: str = arg_not_passed


@dataclass
class textAreaInput(Input):
    input_label: str
    input_name: str
    value: str = arg_not_passed


@dataclass
class emailInput(Input):
    input_label: str
    input_name: str
    value: str = arg_not_passed


@dataclass
class passwordInput(Input):
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


@dataclass
class MaterialAroundTable:
    before_table: ListOfLines
    after_table: ListOfLines

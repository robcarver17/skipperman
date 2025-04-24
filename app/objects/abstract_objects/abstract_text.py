from dataclasses import dataclass
from enum import Enum

from app.objects.utilities.exceptions import arg_not_passed


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
class Heading:
    text: str
    centred: bool = True
    size: int = 1

    @property
    def href(self):
        return self.text.replace(" ", "-").lower()


class LinkToHeading:
    def __init__(
        self,
        heading_text: str,
        link_text_to_show: str = arg_not_passed,
        help_page: str = "",
    ):
        if link_text_to_show is arg_not_passed:
            link_text_to_show = heading_text

        self.heading_text = heading_text
        self.link_text_to_show = link_text_to_show
        self.help_page = help_page

    @property
    def href(self):
        return href_from_name(self.heading_text)


def href_from_name(heading_text: str):
    return heading_text.replace(" ", "-").lower()


class Input:
    input_name: str
    input_name: str


Arrow = Enum(
    "Arrow", ["Up", "Down", "Left", "Right", "UpDown", "LeftRight", "OutlineLeftRight"]
)
up_arrow = Arrow.Up
down_arrow = Arrow.Down
right_arrow = Arrow.Right
left_arrow = Arrow.Left
up_down_arrow = Arrow.UpDown
left_right_arrow = Arrow.LeftRight
outline_left_right_arrow = Arrow.OutlineLeftRight

Symbol = Enum(
    "Symbol",
    ["Copyright", "RegTradeMark", "Lightning", "CircleUpArrow", "Umbrella", "At"],
)
copyright_symbol = Symbol.Copyright
reg_tm_symbol = Symbol.RegTradeMark
lightning_symbol = Symbol.Lightning
circle_up_arrow_symbol = Symbol.CircleUpArrow
umbrella_symbol = Symbol.Umbrella
at_symbol = Symbol.At

Pointer = Enum("Pointer", ["Up", "Down", "Left", "Right"])
up_pointer = Pointer.Up
down_pointer = Pointer.Down
left_pointer = Pointer.Left
right_pointer = Pointer.Right

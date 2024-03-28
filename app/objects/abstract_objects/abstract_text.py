from dataclasses import dataclass
from enum import Enum


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
    size: int= 1

class Input:
    input_name: str
    input_name: str


Arrow = Enum("Arrow", ["Up", "Down", "Left", "Right", "UpDown","LeftRight"])
up_arrow = Arrow.Up
down_arrow = Arrow.Down
right_arrow = Arrow.Right
left_arrow = Arrow.Left
up_down_arrow = Arrow.UpDown
left_right_arrow = Arrow.LeftRight

Symbol = Enum("Symbol", ["Copyright", "RegTradeMark", "Lightning","CircleUpArrow", "Umbrella", "At"])
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

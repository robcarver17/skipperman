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


class Input:
    input_name: str
    input_name: str


Arrow = Enum("Arrow", ["Up", "Down", "Left", "Right"])
up_arrow = Arrow.Up
down_arrow = Arrow.Down
right_arrow = Arrow.Right
left_arrow = Arrow.Left



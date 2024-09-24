from dataclasses import dataclass
from typing import Union

from app.objects_OLD.abstract_objects.abstract_text import Input, Heading
from app.objects_OLD.abstract_objects.abstract_buttons import Button, ButtonBar


class Line(list):
    def __init__(self, passed_list: Union[list, Button, str, Input, Heading]):
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
        return ListOfLines(list(self) + list(other))

    def add_Lines(self):
        new_list = []
        for element in self:
            if (
                type(element) is Line
                or type(element) is ListOfLines
                or type(element) is ButtonBar
            ):
                new_list.append(element)
            else:
                new_list.append(Line(element))

        return ListOfLines(new_list)


_______________ = Line("             ")


@dataclass
class DetailListOfLines:
    list_of_lines: ListOfLines
    name: str = "Detail"
    open: bool = False


@dataclass
class DetailLine:
    string: str
    name: str = "Detail"
    open: bool = False


def make_long_thing_detail_box(some_string: str):
    if len(some_string) > 100:
        return DetailLine(string=some_string, name="Detail")
    else:
        return some_string

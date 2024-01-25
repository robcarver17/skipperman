from typing import Union

from app.objects.abstract_objects.abstract_text import Input
from app.objects.abstract_objects.abstract_buttons import Button


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
        return ListOfLines(list(self) + list(other))


_______________ = Line("")

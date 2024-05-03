from dataclasses import dataclass
from typing import Union, List

from app.objects.abstract_objects.abstract_text import Arrow, Pointer, Symbol
from app.objects.constants import arg_not_passed

MAIN_MENU_BUTTON_LABEL = "Main menu"
CANCEL_BUTTON_LABEL = "Cancel"
FINISHED_BUTTON_LABEL = "Finished"
BACK_BUTTON_LABEL = "Back"


def is_finished_button(button_value: str) -> bool:
    return button_value==FINISHED_BUTTON_LABEL


@dataclass
class Button:
    label: Union[str, 'Line', Arrow, Pointer, Symbol]
    value: str = arg_not_passed
    big: bool = False
    tile: bool = False
    nav_button: bool = False

class ButtonBar(List[Button]):
    def __repr__(self):
        return "ButtonBar contents %s" % str(super().__repr__())

main_menu_button = Button(MAIN_MENU_BUTTON_LABEL)


def get_nav_bar_with_just_back_button() -> ButtonBar:
    back_button = Button(BACK_BUTTON_LABEL,
                         nav_button=True)

    return ButtonBar([back_button])

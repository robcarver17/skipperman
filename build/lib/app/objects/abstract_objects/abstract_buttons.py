from dataclasses import dataclass
from typing import Union, List

from app.data_access.configuration.fixed import (
    MAIN_MENU_KEYBOARD_SHORTCUT,
    HELP_KEYBOARD_SHORTCUT,
    BACK_KEYBOARD_SHORTCUT,
    CANCEL_KEYBOARD_SHORTCUT,
    SAVE_KEYBOARD_SHORTCUT,
)
from app.objects.abstract_objects.abstract_text import Arrow, Pointer, Symbol
from app.objects.exceptions import arg_not_passed

MAIN_MENU_BUTTON_LABEL = "Main menu"
CANCEL_BUTTON_LABEL = "Cancel"
FINISHED_BUTTON_LABEL = "Finished"
_DO_NOT_USE_USE_CANCEL_INSTEAD = "Back (Cancel changes)"
BACK_BUTTON_LABEL = "Back"


def is_finished_button(button_value: str) -> bool:
    return button_value == FINISHED_BUTTON_LABEL


MAIN_MENU = "main_menu"  ## Not actual index page


@dataclass
class Button:
    label: Union[str, "Line", Arrow, Pointer, Symbol]
    value: str = arg_not_passed
    big: bool = False
    tile: bool = False
    nav_button: bool = False
    shortcut: str = arg_not_passed

    @property
    def name(self):
        if self.value is arg_not_passed:
            return self.label
        return self.value

    def pressed(self, last_button: str):
        return self.name == last_button


@dataclass
class MainMenuNavButton:
    label: str = MAIN_MENU_BUTTON_LABEL
    shortcut: str = MAIN_MENU_KEYBOARD_SHORTCUT


@dataclass
class ActionOptionButton:
    label: str
    url: str = ""


@dataclass
class HelpButton:
    help_page: str
    shortcut: str = HELP_KEYBOARD_SHORTCUT
    from_main_menu: bool = False


class ButtonBar(List[Union[HelpButton,Button]]):
    def __repr__(self):
        return "ButtonBar contents %s" % str(super().__repr__())


def get_nav_bar_with_just_back_button() -> ButtonBar:
    return ButtonBar([back_menu_button])


def get_nav_bar_with_just_cancel_button() -> ButtonBar:
    return ButtonBar([cancel_menu_button])


def get_nav_bar_with_just_main_menu_and_back_button() -> ButtonBar:
    return ButtonBar([main_menu_button, back_menu_button])


SAVE_BUTTON_LABEL = "Save changes"

# main_menu_button = Button(MAIN_MENU_BUTTON_LABEL, url = MAIN_MENU, nav_button=True, shortcut=MAIN_MENU_KEYBOARD_SHORTCUT)
main_menu_button = MainMenuNavButton()
back_menu_button = Button(
    BACK_BUTTON_LABEL, nav_button=True, shortcut=BACK_KEYBOARD_SHORTCUT
)
cancel_menu_button = Button(
    CANCEL_BUTTON_LABEL, nav_button=True, shortcut=CANCEL_KEYBOARD_SHORTCUT
)
save_menu_button = Button(
    SAVE_BUTTON_LABEL, nav_button=True, shortcut=SAVE_KEYBOARD_SHORTCUT
)

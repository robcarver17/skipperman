from dataclasses import dataclass

from app.objects.constants import arg_not_passed

MAIN_MENU_BUTTON_LABEL = "Main menu"
CANCEL_BUTTON_LABEL = "Cancel"
FINISHED_BUTTON_LABEL = "Finished"
BACK_BUTTON_LABEL = "Back"


def is_finished_button(button_value: str) -> bool:
    return button_value==FINISHED_BUTTON_LABEL


@dataclass
class Button:
    label: str
    value: str = arg_not_passed
    big: bool = False



main_menu_button = Button(MAIN_MENU_BUTTON_LABEL)

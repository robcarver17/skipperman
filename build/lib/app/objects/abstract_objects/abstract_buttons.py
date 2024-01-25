from dataclasses import dataclass

from app.objects.constants import arg_not_passed

MAIN_MENU_BUTTON_LABEL = "Main menu"
CANCEL_BUTTON_LABEL = "Cancel"
FINISHED_BUTTON_LABEL = "Finished"
BACK_BUTTON_LABEL = "Back"


def button_label_requires_going_back(button_label: str) -> bool:
    return button_label in [CANCEL_BUTTON_LABEL, FINISHED_BUTTON_LABEL]


@dataclass
class Button:
    label: str
    name: str = arg_not_passed
    value: str = arg_not_passed


finished_button = Button(FINISHED_BUTTON_LABEL)
cancel_button = Button(CANCEL_BUTTON_LABEL)
back_button = Button(BACK_BUTTON_LABEL)
main_menu_button = Button(MAIN_MENU_BUTTON_LABEL)

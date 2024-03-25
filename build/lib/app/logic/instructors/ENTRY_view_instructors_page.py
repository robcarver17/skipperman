from typing import Union

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import main_menu_button, Button
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_interface import abstractInterface


def display_form_main_instructors_page(interface: abstractInterface) -> Form:
    lines_inside_form = ListOfLines(
        [
            main_menu_button,
            "Tick sheets and reports for instructors will go here at some point"
        ]
    )

    return Form(lines_inside_form)

def post_form_main_instructors_page(interface: abstractInterface) -> Form:
    return Form()
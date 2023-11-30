from typing import Union

from app.logic.forms_and_interfaces.abstract_form import Form, NewForm, Button, ListOfLines, _______________, main_menu_button
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.logic.reporting.constants import GROUP_ALLOCATION_REPORT_STAGE, GROUP_ALLOCATION_REPORT_BUTTON_LABEL

def display_form_view_of_reports(
interface: abstractInterface
) -> Form:
    lines_inside_form = ListOfLines([
        main_menu_button,
        _______________,
        "Select report to run:",
        _______________,
        Button(GROUP_ALLOCATION_REPORT_BUTTON_LABEL)
        ]
    )

    return Form(lines_inside_form)


def post_form_view_of_reports(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed==GROUP_ALLOCATION_REPORT_BUTTON_LABEL:
        return NewForm(GROUP_ALLOCATION_REPORT_STAGE)
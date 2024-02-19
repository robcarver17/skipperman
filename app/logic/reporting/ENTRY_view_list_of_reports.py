from typing import Union

from app.logic.abstract_logic_api import initial_state_form
from app.logic.reporting.allocations.report_group_allocations import display_form_report_group_allocation
from app.logic.reporting.rota.report_rota import display_form_report_rota
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import main_menu_button, Button
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.reporting.constants import (
    GROUP_ALLOCATION_REPORT_BUTTON_LABEL,
ROTA_REPORT_BUTTON_LABEL,
)
from app.objects.constants import missing_data

## MODIFY THIS TO ADD MORE REPORTS
DICT_OF_REPORT_LABELS_AND_STAGES ={
    GROUP_ALLOCATION_REPORT_BUTTON_LABEL: display_form_report_group_allocation,
    ROTA_REPORT_BUTTON_LABEL: display_form_report_rota
}

list_of_report_labels=list(DICT_OF_REPORT_LABELS_AND_STAGES.keys())
list_of_report_buttons = ListOfLines([Button(label) for label in list_of_report_labels])

def function_given_pressed_button_label(label) -> str:
    return DICT_OF_REPORT_LABELS_AND_STAGES.get(label, missing_data)

def display_form_view_of_reports(interface: abstractInterface) -> Form:
    lines_inside_form = ListOfLines(
        [
            main_menu_button,
            _______________,
            "Select report to run:",
            _______________]+
            list_of_report_buttons
    )

    return Form(lines_inside_form)


def post_form_view_of_reports(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    report_function = function_given_pressed_button_label(button_pressed)
    if report_function is missing_data:
        interface.log_error("Report name %s missing from dict contact support" % button_pressed)
        return initial_state_form

    return interface.get_new_form_given_function(report_function)

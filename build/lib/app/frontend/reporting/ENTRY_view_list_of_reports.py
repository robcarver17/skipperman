from typing import Union, Callable

from app.frontend.form_handler import initial_state_form
from app.frontend.reporting.allocations.report_group_allocations import (
    display_form_report_group_allocation,
)
from app.frontend.reporting.rota.report_rota import display_form_report_rota
from app.frontend.reporting.boats.report_boats import display_form_report_boat
from app.frontend.reporting.rollcall_and_contacts.rollcall_report import (
    display_form_report_rollcall,
)
from app.frontend.reporting.sailors.ENTRY_report_sailors import display_form_for_sailors_report
from app.frontend.reporting.data_dumps.ENTRY_data_dump import (
    display_form_for_data_dump_report,
)
from app.frontend.reporting.all_event_data.ENTRY_all_event_data import (
    display_form_for_all_event_data_report,
)

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import (
    main_menu_button,
    Button,
    ButtonBar,
    HelpButton,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    Line,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.exceptions import missing_data

GROUP_ALLOCATION_REPORT_BUTTON_LABEL = "Group allocation for event"
ROTA_REPORT_BUTTON_LABEL = "Volunteer rota for event"
BOATS_REPORT_BUTTON_LABEL = "Spotter sheet for event"
ROLLCALL_REPORT_BUTTON_LABEL = "Rollcall/health/contacts for event"
SAILORS_DATA_REPORT_BUTTON_LABEL = "Sailors data"
CADET_EVENT_HISTORY_REPORT_BUTTON_LABEL = "Cadet event history"
DUMP_BUTTON_LABEL = "Data dumps"
EVENT_DATA_BUTTON_LABEL = "All event data in giant spreadsheet"

## MODIFY THIS TO ADD MORE REPORTS
DICT_OF_REPORT_LABELS_AND_STAGES = {
    GROUP_ALLOCATION_REPORT_BUTTON_LABEL: display_form_report_group_allocation,
    ROTA_REPORT_BUTTON_LABEL: display_form_report_rota,
    BOATS_REPORT_BUTTON_LABEL: display_form_report_boat,
    ROLLCALL_REPORT_BUTTON_LABEL: display_form_report_rollcall,
    SAILORS_DATA_REPORT_BUTTON_LABEL: display_form_for_sailors_report,
    EVENT_DATA_BUTTON_LABEL: display_form_for_all_event_data_report,
    DUMP_BUTTON_LABEL: display_form_for_data_dump_report,

}

list_of_report_labels = list(DICT_OF_REPORT_LABELS_AND_STAGES.keys())
list_of_report_buttons = Line(
    [Button(label, tile=True) for label in list_of_report_labels]
)
help_button = HelpButton("reporting_help")

nav_buttons = ButtonBar([main_menu_button, help_button])


def function_given_pressed_button_label(label) -> Callable:
    return DICT_OF_REPORT_LABELS_AND_STAGES.get(label, missing_data)


def display_form_view_of_reports(
    interface: abstractInterface,
) -> Form:  ## have to keep interface as standard input
    return Form(ListOfLines([nav_buttons, list_of_report_buttons]))


def post_form_view_of_reports(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    report_function = function_given_pressed_button_label(button_pressed)
    if report_function is missing_data:
        interface.log_error(
            "Report name %s missing from dict contact support" % button_pressed
        )
        return initial_state_form

    return interface.get_new_form_given_function(report_function)

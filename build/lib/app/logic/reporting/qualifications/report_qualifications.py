from typing import Union

from app.logic.reporting.qualifications.achieved_qualifications import \
    write_qualifications_to_temp_csv_file_and_return_filename
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_form import (
    Form,
    File, NewForm, )
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL, Button, ButtonBar, main_menu_button


def display_form_for_qualifications_report(interface: abstractInterface):
    contents_of_form = ListOfLines(
        [
            ButtonBar([main_menu_button, cancel_button]),
            Line([create_report_button, expected_report_button])
        ]
    )

    return Form(contents_of_form)

MAKE_REPORT_BUTTON_LABEL = "Download list of qualifications"
EXPECTED_REPORT_BUTTON_LABEL = "Expected qualifications at event"
cancel_button = Button(BACK_BUTTON_LABEL, nav_button=True)
create_report_button = Button(MAKE_REPORT_BUTTON_LABEL, tile=True) ## tile
expected_report_button = Button(EXPECTED_REPORT_BUTTON_LABEL, tile=True) ## tile

def post_form_for_qualifications_report(
    interface: abstractInterface,
) -> Union[File, Form, NewForm]:
    last_button = interface.last_button_pressed()

    if last_button == BACK_BUTTON_LABEL:
        return previous_form(interface)
    elif last_button == MAKE_REPORT_BUTTON_LABEL:
        filename = write_qualifications_to_temp_csv_file_and_return_filename(interface)
        return File(filename)
    elif last_button== EXPECTED_REPORT_BUTTON_LABEL:
        pass


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(post_form_for_qualifications_report)




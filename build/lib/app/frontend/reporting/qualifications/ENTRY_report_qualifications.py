from app.frontend.reporting.qualifications.achieved_qualifications import (
    write_qualifications_to_temp_csv_file_and_return_filename,
)
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.abstract_objects.abstract_buttons import back_menu_button
from app.frontend.reporting.qualifications.qualification_status import *


def display_form_for_qualifications_report(interface: abstractInterface):
    contents_of_form = ListOfLines(
        [
            ButtonBar([main_menu_button, back_menu_button]),
            Line(
                [
                    create_qualification_list_report_button,
                    expected_qualification_report_button,
                ]
            ),
        ]
    )

    return Form(contents_of_form)


QUALIFICATION_LIST_BUTTON_LABEL = "Download list of qualifications_and_ticks"
STATUS_REPORT_BUTTON_LABEL = "Qualification status at event"
create_qualification_list_report_button = Button(
    QUALIFICATION_LIST_BUTTON_LABEL, tile=True
)  ## tile
expected_qualification_report_button = Button(
    STATUS_REPORT_BUTTON_LABEL, tile=True
)  ## tile


def post_form_for_qualifications_report(
    interface: abstractInterface,
) -> Union[File, Form, NewForm]:
    last_button = interface.last_button_pressed()

    if back_menu_button.pressed(last_button):
        return previous_form(interface)
    elif create_qualification_list_report_button.pressed(last_button):
        filename = write_qualifications_to_temp_csv_file_and_return_filename(interface)
        return File(filename)
    elif expected_qualification_report_button.pressed(last_button):
        return interface.get_new_form_given_function(
            display_form_for_qualification_status_report
        )


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        post_form_for_qualifications_report
    )

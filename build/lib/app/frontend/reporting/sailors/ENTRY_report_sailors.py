from app.frontend.reporting.sailors.achieved_qualifications import (
    write_qualifications_to_temp_csv_file_and_return_filename,
)
from app.backend.groups.cadet_event_history import \
    write_group_history_and_qualification_status_to_temp_csv_file_and_return_filename
from app.objects.abstract_objects.abstract_buttons import HelpButton
from app.objects.abstract_objects.abstract_lines import Line
from app.frontend.reporting.sailors.qualification_status import *


def display_form_for_sailors_report(interface: abstractInterface):
    contents_of_form = ListOfLines(
        [
            ButtonBar([main_menu_button, back_menu_button, help_button]),
            Line(
                [
                    create_qualification_list_report_button,
                    expected_qualification_report_button,
                    history_report_button
                ]
            ),
        ]
    )

    return Form(contents_of_form)

help_button = HelpButton('qualifications_report_help')



QUALIFICATION_LIST_BUTTON_LABEL = "Achieved qualifications"
STATUS_REPORT_BUTTON_LABEL = "Qualification & tick status at event"
GROUP_HISTORY_BUTTON_LABEL = "Group history and qualifications"

create_qualification_list_report_button = Button(
    QUALIFICATION_LIST_BUTTON_LABEL, tile=True
)  ## tile
expected_qualification_report_button = Button(
    STATUS_REPORT_BUTTON_LABEL, tile=True
)  ## tile
history_report_button = Button(GROUP_HISTORY_BUTTON_LABEL, tile=True)

def post_form_for_sailors_report(
    interface: abstractInterface,
) -> Union[File, Form, NewForm]:
    last_button = interface.last_button_pressed()

    if back_menu_button.pressed(last_button):
        return previous_form(interface)
    elif create_qualification_list_report_button.pressed(last_button):
        filename = write_qualifications_to_temp_csv_file_and_return_filename(
            object_store=interface.object_store
        )
        return File(filename)
    elif history_report_button.pressed(last_button):
        filename = write_group_history_and_qualification_status_to_temp_csv_file_and_return_filename(
            object_store=interface.object_store
        )
        return File(filename)

    elif expected_qualification_report_button.pressed(last_button):
        return interface.get_new_form_given_function(
            display_form_for_qualification_status_report
        )


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        post_form_for_sailors_report
    )

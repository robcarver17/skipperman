from app.backend.forms.form_utils import get_availability_checkbox, dropdown_input_for_status_change
from app.backend.wa_import.update_cadets_at_event import new_status_and_status_message, NO_STATUS_CHANGE
from app.logic.events.constants import (
    USE_NEW_DATA_BUTTON_LABEL,
    USE_ORIGINAL_DATA_BUTTON_LABEL,
    USE_DATA_IN_FORM_BUTTON_LABEL, ATTENDANCE, ROW_STATUS)
from app.objects.abstract_objects.abstract_form import (
    Form, )
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________

from app.backend.cadets import cadet_name_from_id
from app.objects.OLDmaster_event import (
    RowInMasterEvent,
)
from app.objects.events import Event

def display_form_for_update_to_existing_row_of_event_data(new_row_in_mapped_wa_event_with_status: RowInMasterEvent,
                                                          existing_row_in_master_event: RowInMasterEvent,
                                                          event: Event) -> Form:
    overall_message = (
        "There have been important changes for event registration information about cadet %s"
        % cadet_name_from_id(existing_row_in_master_event.cadet_id)
    )

    status_change_field = get_line_in_form_for_status_change(
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
        existing_row_in_master_event=existing_row_in_master_event,
    )

    attendance_change_field = get_line_in_form_for_attendance_change(
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
        existing_row_in_master_event=existing_row_in_master_event,
        event=event
    )

    buttons = buttons_for_update_row()

    form = Form(
        ListOfLines(
            [
                overall_message,
                _______________,
                status_change_field,
                _______________,
                attendance_change_field,
                _______________,
                _______________,
                buttons,
            ]
        )
    )

    return form


def buttons_for_update_row() -> Line:
    use_new_data = Button(USE_NEW_DATA_BUTTON_LABEL)
    use_original_data = Button(USE_ORIGINAL_DATA_BUTTON_LABEL)
    use_data_in_form = Button(USE_DATA_IN_FORM_BUTTON_LABEL)

    return Line([use_original_data, use_new_data, use_data_in_form])


def get_line_in_form_for_attendance_change(
    new_row_in_mapped_wa_event_with_status: RowInMasterEvent,
    existing_row_in_master_event: RowInMasterEvent,
        event: Event
) -> ListOfLines:

    original_attendance = existing_row_in_master_event.attendance
    new_attendance = new_row_in_mapped_wa_event_with_status.attendance

    header_line = Line("Originally was attending %s, now attending %s" % (str(original_attendance), str(new_attendance)))
    checkbox = get_availability_checkbox(new_attendance,
                                         event=event,
                                         input_name=ATTENDANCE,
                                         input_label="Select days attending:")
    return ListOfLines([
        header_line,
        checkbox
    ])


def get_line_in_form_for_status_change(
    new_row_in_mapped_wa_event_with_status: RowInMasterEvent,
    existing_row_in_master_event: RowInMasterEvent,
) -> Line:
    new_status, status_message = new_status_and_status_message(
        existing_row_in_master_event=existing_row_in_master_event,
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
    )

    if status_message is NO_STATUS_CHANGE:
        return Line(
            [dropdown_input_for_status_change(
                input_name=ROW_STATUS,
                input_label="Status of entry",
                default_status=new_status,
                dict_of_options={new_status.name: new_status.name},## only one option available

            )]
        )
    else:
        return Line(
            [
                dropdown_input_for_status_change(
                    input_label="%s: select status" % status_message,
                    default_status=new_status,
                input_name=ROW_STATUS) ## no dict passed, so all options will be on the table

                ]
        )

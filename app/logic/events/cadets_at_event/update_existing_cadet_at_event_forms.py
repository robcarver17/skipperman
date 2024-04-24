from typing import Union

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

from app.backend.cadets import DEPRECATED_cadet_name_from_id, cadet_name_from_id
from app.objects.cadet_at_event import CadetAtEvent
from app.objects.events import Event

def display_form_for_update_to_existing_cadet_at_event(
        new_cadet_at_event: CadetAtEvent,
                                                        existing_cadet_at_event: CadetAtEvent,
                                                       event: Event) -> Form:
    overall_message = (
        "There have been important changes for event registration information about cadet %s"
        % cadet_name_from_id(existing_cadet_at_event.cadet_id)
    )

    status_change_field = get_line_in_form_for_status_change(
        new_cadet_at_event=new_cadet_at_event,
        existing_cadet_at_event=existing_cadet_at_event,
    )

    attendance_change_field = get_line_in_form_for_attendance_change(
        new_cadet_at_event=new_cadet_at_event,
        existing_cadet_at_event=existing_cadet_at_event,
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
        new_cadet_at_event: CadetAtEvent,
        existing_cadet_at_event: CadetAtEvent,
        event: Event
) -> Union[ListOfLines, Line]:

    original_attendance = existing_cadet_at_event.availability
    new_attendance = new_cadet_at_event.availability

    if original_attendance==new_attendance:
        return Line("Attendance at event %s (unchanged)" % str(new_attendance))

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
        new_cadet_at_event: CadetAtEvent,
        existing_cadet_at_event: CadetAtEvent,
) -> Line:
    new_status, status_message = new_status_and_status_message(
    new_cadet_at_event=new_cadet_at_event,
        existing_cadet_at_event=existing_cadet_at_event
        )

    if status_message is NO_STATUS_CHANGE:
        return Line("Status (unchanged): %s" % new_status.name)

    else:
        return Line(
            [
                dropdown_input_for_status_change(
                    input_label="%s: select status" % status_message,
                    default_status=new_status,
                input_name=ROW_STATUS) ## no dict passed, so all shared will be on the table

                ]
        )

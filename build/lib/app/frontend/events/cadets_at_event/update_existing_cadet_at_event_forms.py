from typing import Union

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.frontend.forms.form_utils import (
    get_availability_checkbox,
    dropdown_input_for_status_change,
)
from app.backend.registration_data.update_cadets_at_event import NO_STATUS_CHANGE, new_status_and_status_message
from app.frontend.events.constants import (
    ATTENDANCE,
    ROW_STATUS,
)
from app.frontend.events.cadets_at_event.update_existing_cadet_at_event_forms import USE_ORIGINAL_DATA_BUTTON_LABEL, \
    USE_NEW_DATA_BUTTON_LABEL, USE_DATA_IN_FORM_BUTTON_LABEL
from app.objects.abstract_objects.abstract_form import (
    Form,
)
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)

from app.OLD_backend.cadets import cadet_name_from_id
from app.objects.cadet_with_id_at_event import CadetWithIdAtEvent
from app.objects.events import Event


def display_form_for_update_to_existing_cadet_at_event(
    interface: abstractInterface,
    new_cadet_at_event: CadetWithIdAtEvent,
    existing_cadet_at_event: CadetWithIdAtEvent,
    event: Event,
) -> Form:
    overall_message = (
        "There have been important changes for event registration information about cadet %s"
        % cadet_name_from_id(
            data_layer=interface.data, cadet_id=existing_cadet_at_event.cadet_id
        )
    )

    status_change_field = get_line_in_form_for_status_change(
        interface=interface,
        new_cadet_at_event=new_cadet_at_event,
        existing_cadet_at_event=existing_cadet_at_event,
    )

    attendance_change_field = get_line_in_form_for_attendance_change(
        new_cadet_at_event=new_cadet_at_event,
        existing_cadet_at_event=existing_cadet_at_event,
        event=event,
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
    new_cadet_at_event: CadetWithIdAtEvent,
    existing_cadet_at_event: CadetWithIdAtEvent,
    event: Event,
) -> Union[ListOfLines, Line]:
    original_attendance = existing_cadet_at_event.availability
    new_attendance = new_cadet_at_event.availability

    if original_attendance == new_attendance:
        return Line("Attendance at event %s (unchanged)" % str(new_attendance))

    header_line = Line(
        "Originally was attending %s, now attending %s"
        % (str(original_attendance), str(new_attendance))
    )
    checkbox = get_availability_checkbox(
        new_attendance,
        event=event,
        input_name=ATTENDANCE,
        input_label="Select days attending:",
    )
    return ListOfLines([header_line, checkbox])


def get_line_in_form_for_status_change(
    interface: abstractInterface,
    new_cadet_at_event: CadetWithIdAtEvent,
    existing_cadet_at_event: CadetWithIdAtEvent,
) -> Line:
    new_status, status_message = new_status_and_status_message(
        interface=interface,
        new_cadet_at_event=new_cadet_at_event,
        existing_cadet_at_event=existing_cadet_at_event,
    )

    if status_message is NO_STATUS_CHANGE:
        return Line("Status (unchanged): %s" % new_status.name)

    else:
        return Line(
            [
                dropdown_input_for_status_change(
                    input_label="%s: select status" % status_message,
                    default_status=new_status,
                    input_name=ROW_STATUS,
                )  ## no dict passed, so all shared will be on the table
            ]
        )

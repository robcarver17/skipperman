from typing import Union

from app.objects.cadets import Cadet


from app.frontend.forms.form_utils import (
    get_availability_checkbox,
    dropdown_input_for_status_change,
)
from app.backend.registration_data.update_cadets_at_event import (
    NO_STATUS_CHANGE,
    new_status_and_status_message,
)
from app.frontend.events.constants import (
    ATTENDANCE,
    ROW_STATUS,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
)
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)

from app.objects.cadet_with_id_at_event import CadetWithIdAtEvent
from app.objects.events import Event


def display_form_for_update_to_existing_cadet_at_event(
    cadet: Cadet,
    new_cadet_at_event_data: CadetWithIdAtEvent,
    existing_cadet_at_event_data: CadetWithIdAtEvent,
    event: Event,
) -> Form:
    overall_message = (
        "There have been important changes for event registration information about cadet %s"
        % cadet
    )

    status_change_field = get_line_in_form_for_status_change(
        cadet=cadet,
        new_cadet_at_event_data=new_cadet_at_event_data,
        existing_cadet_at_event_data=existing_cadet_at_event_data,
    )

    attendance_change_field = get_line_in_form_for_attendance_change(
        new_cadet_at_event_data=new_cadet_at_event_data,
        existing_cadet_at_event_data=existing_cadet_at_event_data,
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

    return Line(
        [use_original_data_button, use_data_in_form_button,  use_new_data_button]
    )


USE_NEW_DATA_BUTTON_LABEL = "Use new data imported from latest file (recommended)"
use_new_data_button = Button(USE_NEW_DATA_BUTTON_LABEL)
USE_ORIGINAL_DATA_BUTTON_LABEL = (
    "Use original data that we already have (ignores subsequent changes in file)"
)
use_original_data_button = Button(USE_ORIGINAL_DATA_BUTTON_LABEL)
USE_DATA_IN_FORM_BUTTON_LABEL = "Use data as edited in form above (will be newest data from file if no changes made in form)"
use_data_in_form_button = Button(USE_DATA_IN_FORM_BUTTON_LABEL)


def get_line_in_form_for_attendance_change(
    new_cadet_at_event_data: CadetWithIdAtEvent,
    existing_cadet_at_event_data: CadetWithIdAtEvent,
    event: Event,
) -> Union[ListOfLines, Line]:
    original_attendance = existing_cadet_at_event_data.availability.days_available_as_str()
    new_attendance = new_cadet_at_event_data.availability.days_available_as_str()

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
    cadet: Cadet,
    new_cadet_at_event_data: CadetWithIdAtEvent,
    existing_cadet_at_event_data: CadetWithIdAtEvent,
) -> Line:
    new_status, status_message = new_status_and_status_message(
        cadet=cadet,
        new_cadet_at_event_data=new_cadet_at_event_data,
        existing_cadet_at_event_data=existing_cadet_at_event_data,
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

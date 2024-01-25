from app.logic.events.constants import (
    USE_NEW_DATA_BUTTON_LABEL,
    USE_ORIGINAL_DATA_BUTTON_LABEL,
    USE_DATA_IN_FORM_BUTTON_LABEL,
)
from app.logic.events.update_master.other_fields_in_master_event_data_update import \
    get_lines_in_form_for_other_differences
from app.logic.events.update_master.status_fields_in_master_event_data_update import get_line_in_form_for_status_change
from app.objects.abstract_objects.abstract_form import (
    Form,
)
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines

from app.backend.cadets import cadet_name_from_id
from app.objects.master_event import (
    RowInMasterEvent,
)


def display_form_for_update_to_existing_row_of_event_data(new_row_in_mapped_wa_event_with_status: RowInMasterEvent,
                                                          existing_row_in_master_event: RowInMasterEvent) -> Form:
    overall_message = (
        "There have been important changes for event registration information about cadet %s"
        % cadet_name_from_id(existing_row_in_master_event.cadet_id)
    )

    status_change_field = get_line_in_form_for_status_change(
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
        existing_row_in_master_event=existing_row_in_master_event,
    )

    form_fields_with_other_differences = get_lines_in_form_for_other_differences(
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
        existing_row_in_master_event=existing_row_in_master_event,
    )

    buttons = buttons_for_update_row()

    form = Form(
        ListOfLines(
            [
                overall_message,
                status_change_field,
                form_fields_with_other_differences,
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







from typing import Union

from app.logic.events.backend.map_wa_fields import get_wa_field_mapping_dict
from app.logic.forms_and_interfaces.abstract_form import (
    Form,
    NewForm,
Line,
ListOfLines,
_______________
)
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.logic.events.utilities import get_event_from_state
from app.logic.events.backend.load_wa_file import does_raw_event_file_exist, load_raw_wa_file
from app.logic.forms_and_interfaces.abstract_interface import (
    form_with_message_and_finished_button,
form_with_content_and_finished_button
)
from app.logic.events.backend.load_wa_file import (
    get_staged_file_raw_event_filename,
)
from app.objects.events import Event
from app.objects.field_list import ALL_FIELDS_EXPECTED_IN_WA_FILE
from app.objects.utils import in_x_not_in_y


def display_form_check_field_mapping(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    if not does_raw_event_file_exist(event_id=event.id):
        return form_with_message_and_finished_button(message="You can only check mapping AFTER you have uploaded a WA file, but BEFORE you have imported it: go back to event and import a file", interface=interface)

    ## get the raw event file
    filename = get_staged_file_raw_event_filename(event.id)
    warning_list = list_of_warnings_about_fields(event, filename)

    return form_with_content_and_finished_button(warning_list, interface=interface)

def post_form_check_field_mapping(interface: abstractInterface) -> Union[Form, NewForm]:
    raise Exception("Should never be reached!")


def list_of_warnings_about_fields(
    event: Event,
        filename: str,
) -> ListOfLines:
    wa_as_df = load_raw_wa_file(filename)
    # Set up WA event mapping fields
    wa_field_mapping = get_wa_field_mapping_dict(event=event)

    fields_in_wa_file = list(wa_as_df.columns)
    in_mapping_not_in_wa_file = wa_field_mapping.wa_fields_missing_from_list(
        fields_in_wa_file
    )
    in_wa_file_not_in_mapping = wa_field_mapping.wa_fields_missing_from_mapping(
        fields_in_wa_file
    )
    expected_not_in_mapping = in_x_not_in_y(ALL_FIELDS_EXPECTED_IN_WA_FILE, wa_field_mapping.list_of_skipperman_fields)

    output = []
    if len(in_mapping_not_in_wa_file)>0:
        output.append(Line(
            "Following fields are missing from WA file; may cause problems later: %s\n" % ", ".join(in_mapping_not_in_wa_file)))
        output.append(_______________)

    if len(in_wa_file_not_in_mapping) > 0:
        output.append(Line(
            "Following fields are in WA file but will not be imported, probably OK: %s\n" % ", ".join(in_wa_file_not_in_mapping)))
        output.append(_______________)

    if len(expected_not_in_mapping) > 0:
        output.append(Line(
            "Following internal fields are not defined in mapping file, might be OK depending on event type: %s\n" % ", ".join(expected_not_in_mapping)))

    if len(output)==0:
        output = [Line("No problems with mapping")]

    return ListOfLines(output)

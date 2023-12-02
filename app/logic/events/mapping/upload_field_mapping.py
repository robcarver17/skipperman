from app.logic.events.mapping.read_and_write_mapping_files import (
    write_field_mapping_for_event,
    read_mapping_from_csv_file_object,
)
from app.logic.forms_and_interfaces.abstract_interface import (
    abstractInterface,
    get_file_from_interface,
    form_with_message_and_finished_button,
)
from app.logic.forms_and_interfaces.abstract_form import (
    cancel_button,
    Form,
    ListOfLines,
    Line,
    Button,
    fileInput,
)
from app.logic.events.utilities import get_event_from_state
from app.logic.abstract_logic_api import initial_state_form
from app.logic.events.constants import UPLOAD_FILE_BUTTON_LABEL, MAPPING_FILE


def display_form_for_upload_custom_field_mapping(interface: abstractInterface):
    buttons = get_upload_buttons()
    file_select_field = fileInput(input_label=MAPPING_FILE, accept=".csv")

    list_of_lines = ListOfLines(
        ["Choose .csv file to upload for field mapping", file_select_field, buttons]
    )

    return Form(list_of_lines)


def get_upload_buttons():
    upload = Button(UPLOAD_FILE_BUTTON_LABEL)

    return Line([cancel_button, upload])


def post_form_for_upload_custom_field_mapping(interface: abstractInterface):
    try:
        file = get_file_from_interface(MAPPING_FILE, interface=interface)
        mapping = read_mapping_from_csv_file_object(file)
    except Exception as e:
        interface.log_error("Something went wrong uploading file %s" % str(e))
        return initial_state_form

    event = get_event_from_state(interface)
    write_field_mapping_for_event(event=event, new_mapping=mapping)

    return form_with_message_and_finished_button(
        "Uploaded new mapping for event %s" % str(event), interface=interface
    )

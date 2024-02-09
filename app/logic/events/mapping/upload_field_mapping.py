from app.backend.data.field_mapping import write_field_mapping_for_event, read_mapping_from_csv_file_object
from app.logic.abstract_interface import (
    abstractInterface,
    get_file_from_interface,
    form_with_message_and_finished_button,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    fileInput, NewForm,
)
from app.objects.abstract_objects.abstract_buttons import CANCEL_BUTTON_LABEL, Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.logic.events.events_in_state import get_event_from_state
from app.logic.abstract_logic_api import initial_state_form
from app.logic.events.constants import UPLOAD_FILE_BUTTON_LABEL, MAPPING_FILE, WA_FIELD_MAPPING_IN_VIEW_EVENT_STAGE


def display_form_for_upload_custom_field_mapping(interface: abstractInterface):
    buttons = get_upload_buttons()
    file_select_field = fileInput(input_name=MAPPING_FILE, accept=".csv")
    event = get_event_from_state(interface)

    list_of_lines = ListOfLines(
        ["Choose .csv file to upload for field mapping of event %s" % str(event), file_select_field, buttons]
    )

    return Form(list_of_lines)


def get_upload_buttons():
    upload = Button(UPLOAD_FILE_BUTTON_LABEL)

    return Line([cancel_button, upload])

cancel_button = Button(CANCEL_BUTTON_LABEL)

def post_form_for_upload_custom_field_mapping(interface: abstractInterface):
    if interface.last_button_pressed()==CANCEL_BUTTON_LABEL:
        return NewForm(WA_FIELD_MAPPING_IN_VIEW_EVENT_STAGE)
    try:
        file = get_file_from_interface(MAPPING_FILE, interface=interface)
        mapping = read_mapping_from_csv_file_object(file)
        event = get_event_from_state(interface)
        write_field_mapping_for_event(event=event, new_mapping=mapping)
    except Exception as e:
        interface.log_error("Something went wrong uploading file %s" % str(e))
        return NewForm(WA_FIELD_MAPPING_IN_VIEW_EVENT_STAGE)

    return form_with_message_and_finished_button(
        "Uploaded new mapping for event %s" % str(event), interface=interface,
        set_stage_name_to_go_to_on_button_press=WA_FIELD_MAPPING_IN_VIEW_EVENT_STAGE
    )

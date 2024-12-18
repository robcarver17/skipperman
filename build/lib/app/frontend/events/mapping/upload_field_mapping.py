from app.backend.mapping.list_of_field_mappings import save_field_mapping_for_event
from app.data_access.csv.wa_field_mapping import read_mapping_from_csv_file_object
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface, form_with_message_and_finished_button, get_file_from_interface,
)
from app.objects.abstract_objects.abstract_form import Form, fileInput
from app.objects.abstract_objects.abstract_buttons import (
    cancel_menu_button,
    Button,
    ButtonBar,
)
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.frontend.shared.events_state import get_event_from_state



def display_form_for_upload_custom_field_mapping(interface: abstractInterface):
    buttons = get_upload_buttons()
    file_select_field = fileInput(input_name=MAPPING_FILE, accept=".csv")
    event = get_event_from_state(interface)

    list_of_lines = ListOfLines(
        [
            Line(
                "Choose .csv file to upload for field mapping of event %s" % str(event)
            ),
            Line(file_select_field),
            buttons,
        ]
    )

    return Form(list_of_lines)


def get_upload_buttons():
    return ButtonBar([cancel_menu_button, upload_button])

UPLOAD_FILE_BUTTON_LABEL = "Upload file"
upload_button = Button(UPLOAD_FILE_BUTTON_LABEL, nav_button=True)


def post_form_for_upload_custom_field_mapping(interface: abstractInterface):
    previous_form = interface.get_new_display_form_for_parent_of_function(
        display_form_for_upload_custom_field_mapping
    )
    if interface.last_button_pressed() == cancel_menu_button.label:
        return previous_form
    try:
        file = get_file_from_interface(MAPPING_FILE, interface=interface)
        mapping = read_mapping_from_csv_file_object(file)
        event = get_event_from_state(interface)
        save_field_mapping_for_event(
            object_store=interface.object_store, event=event, mapping=mapping
        )
        interface.flush_cache_to_store()

    except Exception as e:
        interface.log_error("Something went wrong uploading file %s" % str(e))
        return previous_form

    return form_with_message_and_finished_button(
        "Uploaded new mapping for event %s" % str(event),
        interface=interface,
        function_whose_parent_go_to_on_button_press=display_form_for_upload_custom_field_mapping,
    )

MAPPING_FILE = "mapping_File"
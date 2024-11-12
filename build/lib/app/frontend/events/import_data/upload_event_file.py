import os
from typing import Union

from app.data_access.configuration.configuration import ALLOWED_UPLOAD_FILE_TYPES
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    fileInput,
)
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
)
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.objects.abstract_objects.abstract_buttons import cancel_menu_button
from app.frontend.form_handler import (
    initial_state_form,
    button_error_and_back_to_initial_state_form,
)
from app.backend.wild_apricot.load_wa_file import (
    save_staged_file_of_raw_event_upload_with_event_id,
    check_local_file_is_valid_wa_file,
    WA_FILE,
)
from app.backend.file_handling import (
    verify_and_return_uploaded_wa_event_file,
    save_uploaded_file_as_local_temp_file,
)
from app.backend.mapping.event_mapping import verify_and_if_required_add_wa_mapping
from app.frontend.shared.events_state import get_event_from_state


def display_form_upload_event_file(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    return get_form_for_wa_upload_with_prompt(
        "Select exported WA file for event %s" % str(event)
    )


def get_form_for_wa_upload_with_prompt(prompt: str) -> Form:
    buttons = get_upload_buttons()
    input_field = fileInput(input_name=WA_FILE, accept=ALLOWED_UPLOAD_FILE_TYPES)

    list_of_lines = ListOfLines([Line(prompt), Line(input_field), buttons])

    return Form(list_of_lines)


def get_upload_buttons():
    upload = Button(UPLOAD_FILE_BUTTON_LABEL, nav_button=True)

    return ButtonBar([cancel_menu_button, upload])

def post_form_upload_event_file(interface: abstractInterface,
                                ) -> Union[Form, NewForm]:

    button_pressed = interface.last_button_pressed()

    if upload_button.pressed(button_pressed):
        return respond_to_uploaded_file(interface)
    elif cancel_menu_button.pressed(button_pressed):
        return interface.get_new_display_form_for_parent_of_function(post_form_upload_event_file)
    else:
        button_error_and_back_to_initial_state_form(interface)



def respond_to_uploaded_file(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        verify_uploaded_wa_file_and_save_as_staged_file(interface)
    except Exception as e:
        ## revert to view events
        interface.log_error("Problem with file upload %s" % e)
        return initial_state_form

    return form_with_message_and_finished_button(
        "Uploaded file successfully",
        interface=interface,
        function_whose_parent_go_to_on_button_press=display_form_upload_event_file,
    )


def verify_uploaded_wa_file_and_save_as_staged_file(interface: abstractInterface):
    temp_filename = verify_and_save_uploaded_wa_event_file_as_temporary_file(interface)
    try:
        event = get_event_from_state(interface)

        verify_and_if_required_add_wa_mapping(
            object_store=interface.object_store, filename=temp_filename, event=event
        )
        save_staged_file_of_raw_event_upload_with_event_id(
            temp_filename, event=event
        )
    except Exception as e:
        os.remove(temp_filename)
        raise e

    os.remove(temp_filename)


def verify_and_save_uploaded_wa_event_file_as_temporary_file(
    interface: abstractInterface,
) -> str:
    ## returns local filename, ensuring we don't overwrite
    ## does not check is a valid WA file
    ## not associated with event so just given incremental filename
    file = verify_and_return_uploaded_wa_event_file(interface=interface, file_marker_name=WA_FILE)
    temp_filename = save_uploaded_file_as_local_temp_file(file)
    check_local_file_is_valid_wa_file(temp_filename)

    return temp_filename

UPLOAD_FILE_BUTTON_LABEL = "Upload selected file"
upload_button = Button(UPLOAD_FILE_BUTTON_LABEL)
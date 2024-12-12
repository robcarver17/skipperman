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
    BACK_BUTTON_LABEL,
    Button,
    ButtonBar,
)
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface, form_with_message_and_finished_button,
)
from app.objects.abstract_objects.abstract_buttons import back_menu_button
from app.frontend.form_handler import (
    initial_state_form,
    button_error_and_back_to_initial_state_form,
)
from app.frontend.events.constants import UPLOAD_FILE_BUTTON_LABEL
from app.backend.wild_apricot.load_wa_file import (
    save_staged_file_of_raw_event_upload_with_event_id,
    check_local_file_is_valid_wa_file,
    WA_FILE,
)
from app.backend.file_handling import verify_and_return_uploaded_wa_event_file, save_uploaded_file_as_local_temp_file
from app.backend.mapping.event_mapping import verify_file_has_correct_wa_id
from app.frontend.shared.events_state import get_event_from_state
from app.objects.events import Event


def display_form_upload_event_file(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    return get_form_for_wa_upload(event=event)


def get_form_for_wa_upload(event: Event) -> Union[Form, NewForm]:
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

    return ButtonBar([back_menu_button, upload])


def post_form_upload_event_file(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    button_pressed = interface.last_button_pressed()
    ## check button pressed (can only be upload or back - anything else treat as back as must be an error)
    if button_pressed == UPLOAD_FILE_BUTTON_LABEL:
        return respond_to_uploaded_file(interface)
    elif button_pressed == BACK_BUTTON_LABEL:
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)


def previous_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_form_upload_event_file
    )


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
        verify_file_has_correct_wa_id(
            interface=interface, filename=temp_filename, event=event
        )
        save_staged_file_of_raw_event_upload_with_event_id(
            temp_filename, event_id=event.id
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
    file = verify_and_return_uploaded_wa_event_file(interface)
    temp_filename = save_uploaded_file_as_local_temp_file(file)
    check_local_file_is_valid_wa_file(temp_filename)

    return temp_filename

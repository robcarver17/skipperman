from typing import Union

import os

from app.data_access.configuration.configuration import WILD_APRICOT_FILE_TYPES
from app.data_access.uploads_and_downloads import get_next_valid_upload_file_name
from app.logic.abstract_form import Form, NewForm, Line, ListOfLines, form_with_message_and_finished_button, Button, back_button, fileInput
from app.logic.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import initial_state_form
from app.logic.events.constants import WA_FILE, UPLOAD_FILE_BUTTON_LABEL
from app.logic.events.backend.load_wa_file import save_staged_file_of_raw_event_upload_with_event_id, load_raw_wa_file, get_event_id_from_wa_df
from app.logic.events.backend.map_wa_files import verify_and_if_required_add_wa_mapping
from app.logic.events.utilities import get_event_from_state
from app.objects.constants import NoFileUploaded, FileError
from app.objects.events import Event

def display_form_upload_event_file(
    interface: abstractInterface
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    return get_form_for_wa_upload(event=event)

def get_form_for_wa_upload(event: Event
) -> Union[Form, NewForm]:
    return get_form_for_wa_upload_with_prompt(
        "Select exported WA file for event %s" % str(event)
    )

def get_form_for_wa_upload_with_prompt(prompt: str)-> Form:
    buttons = get_upload_buttons()
    input_field = fileInput(input_label=WA_FILE, accept=WILD_APRICOT_FILE_TYPES)

    list_of_lines = ListOfLines([prompt, input_field, buttons])

    return Form(list_of_lines)


def get_upload_buttons():
    upload = Button(UPLOAD_FILE_BUTTON_LABEL)

    return Line([back_button, upload])

def post_form_upload_event_file(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    button_pressed = interface.last_button_pressed()
    ## check button pressed (can only be upload or back - anything else treat as back as must be an error)
    if button_pressed == UPLOAD_FILE_BUTTON_LABEL:
        return respond_to_uploaded_file(interface)
    else:
        interface.log_error("Uknown button %s pressed" % button_pressed)
        return initial_state_form

def respond_to_uploaded_file(interface: abstractInterface) -> Union[Form, NewForm]:

    try:
        upload_wa_file_and_save_as_raw_event_with_mapping(interface)
    except Exception as e:
        ## revert to view events
        interface.log_error("Problem with file upload %s" % e)
        return initial_state_form

    return form_with_message_and_finished_button("Uploaded file successfully")



def upload_wa_file_and_save_as_raw_event_with_mapping(interface: abstractInterface):
    local_filename = verify_and_save_uploaded_wa_event_file(interface)
    event = get_event_from_state(interface)
    verify_and_if_required_add_wa_mapping(filename=local_filename, event=event)
    save_staged_file_of_raw_event_upload_with_event_id(local_filename, event_id=event.id)


def verify_and_save_uploaded_wa_event_file(interface: abstractInterface) -> str:
    ## returns local filename, ensuring we don't overwrite
    ## does not check is a valid WA file
    ## not associated with event so just given incremental filename
    file=verify_and_return_uploaded_wa_event_file(interface)
    new_filename = save_uploaded_wa_as_local_file(file)
    check_local_file_is_valid_wa_file(new_filename)

    return new_filename


def verify_and_return_uploaded_wa_event_file(interface: abstractInterface):
    try:
        file = interface.uploaded_file(WA_FILE)
    except NoFileUploaded:
        raise FileError("No file uploaded")

    if file.filename == "":
        raise FileError("No file name selected")

    file_ext = os.path.splitext(file.filename)[1]
    if file_ext not in WILD_APRICOT_FILE_TYPES:
        raise FileError(
            "Not one of file types %s, upload a different file or "
            % WILD_APRICOT_FILE_TYPES
        )

    return file


def save_uploaded_wa_as_local_file(file) -> str:
    new_filename = get_next_valid_upload_file_name(
        "WA_file"
    )  ## don't need to use this anywhere else so can hard code

    try:
        file.save(new_filename)
    except Exception as e:
        raise FileError(
            "Issue %s saving to filename %s- *CONTACT SUPPORT*" % (str(e), new_filename)
        )

    return new_filename


def check_local_file_is_valid_wa_file(new_filename: str):
    ## check can load as a WA file
    try:
        wa_df = load_raw_wa_file(new_filename)
        get_event_id_from_wa_df(wa_df)
    except Exception as e:
        raise FileError("File is not a valid WA event file, error %s" % str(e))
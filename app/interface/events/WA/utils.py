import os

from app.data_access.configuration.configuration import WILD_APRICOT_FILE_TYPES
from app.data_access.uploads_and_downloads import get_next_valid_upload_file_name
from app.interface.events.constants import (
    WA_FILE,
    BACK_BUTTON_LABEL,
    UPLOAD_FILE_LABEL,
    VIEW_EVENT_STAGE,
)
from app.interface.events.utils import get_event_from_state
from app.interface.events.view_events import display_view_of_events
from app.interface.flask.flash import flash_error
from app.interface.flask.state_for_action import StateDataForAction

from app.interface.html.forms import form_html_wrapper, html_file_input, html_button
from app.interface.html.html import (
    Html,
    html_joined_list_as_paragraphs,
    html_joined_list,
)
from app.logic.events.load_wa_file import (
    load_raw_wa_file,
    get_event_id_from_wa_df,
    save_raw_event_upload_with_event_id,
    delete_raw_event_upload_with_event_id,
)
from app.logic.events.map_wa_files import verify_and_if_required_add_wa_mapping
from app.objects.constants import NoFileUploaded, FileError
from app.objects.events import Event


def get_form_for_wa_upload(event: Event, state_data: StateDataForAction):
    html_inside_form = html_inside_form_for_wa_file_upload(
        "Select exported WA file for event %s" % str(event)
    )
    form = form_html_wrapper(state_data.current_url)

    return form.wrap_around(html_inside_form)


def html_inside_form_for_wa_file_upload(display_str: str):
    prompt = Html(display_str)
    buttons = get_upload_buttons()
    input_field = html_file_input(WA_FILE, accept=WILD_APRICOT_FILE_TYPES)

    list_of_html_inside_form = [prompt, input_field, buttons]
    html_inside_form = html_joined_list_as_paragraphs(list_of_html_inside_form)

    return html_inside_form


def get_upload_buttons():
    back = html_button(BACK_BUTTON_LABEL)
    upload = html_button(UPLOAD_FILE_LABEL)

    return html_joined_list([back, upload])


def upload_wa_file_and_save_as_raw_event_with_mapping(state_data: StateDataForAction):
    filename = verify_and_save_uploaded_wa_event_file(state_data=state_data)
    event = get_event_from_state(state_data)
    verify_and_if_required_add_wa_mapping(filename=filename, event=event)
    save_raw_event_upload_with_event_id(filename, event_id=event.id)


def verify_and_save_uploaded_wa_event_file(state_data: StateDataForAction) -> str:
    ## returns local filename, ensuring we don't overwrite
    ## does not check is a valid WA file
    ## not associated with event so just given incremental filename
    file = verify_and_return_uploaded_wa_event_file(state_data)
    new_filename = save_uploaded_wa_as_local_file(file)
    check_local_file_is_valid_wa_file(new_filename)

    return new_filename


def verify_and_return_uploaded_wa_event_file(state_data: StateDataForAction):
    try:
        file = state_data.uploaded_file(WA_FILE)
    except NoFileUploaded:
        raise FileError("No file uploaded")

    if file.filename == "":
        raise FileError("No file name")

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


def reset_stage_and_return_previous(
    state_data: StateDataForAction, error_msg: str = ""
):
    if error_msg is not "":
        flash_error(error_msg)
    state_data.clear_session_data_for_action_and_reset_stage()
    return display_view_of_events(state_data)


def delete_staged_file_for_current_event(state_data: StateDataForAction):
    event = get_event_from_state(state_data)
    delete_raw_event_upload_with_event_id(event.id)

import os

from app.data_access.configuration.configuration import WILD_APRICOT_FILE_TYPES
from app.data_access.uploads_and_downloads import get_next_valid_upload_file_name
from app.web.events.constants import WA_FILE
from app.web.events.utils import get_event_from_state
from app.web.flask.state_for_action import StateDataForAction
from app.backend.wa_import.load_wa_file import save_staged_file_of_raw_event_upload_with_event_id, load_raw_wa_file, get_event_id_from_wa_df
from app.backend.wa_import.map_wa_files import verify_and_if_required_add_wa_mapping
from app.objects.constants import NoFileUploaded, FileError


def upload_wa_file_and_save_as_raw_event_with_mapping(state_data: StateDataForAction):
    local_filename = verify_and_save_uploaded_wa_event_file(state_data=state_data)
    event = get_event_from_state(state_data)
    verify_and_if_required_add_wa_mapping(filename=local_filename, event=event)
    save_staged_file_of_raw_event_upload_with_event_id(local_filename, event_id=event.id)


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
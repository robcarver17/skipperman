import os

import pandas as pd
from app.data_access.file_access import upload_directory

from app.data_access.configuration.configuration import ALLOWED_UPLOAD_FILE_TYPES
from app.data_access.uploads_and_downloads import get_next_valid_upload_file_name
from app.data_access.xls_and_csv import load_spreadsheet_file
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface, get_file_from_interface, )
from app.objects.exceptions import FileError


def create_local_file_from_uploaded_and_return_filename(
    interface: abstractInterface, file_marker_name: str
) -> str:
    original_file = verify_and_return_uploaded_wa_event_file(
        interface=interface, file_marker_name=file_marker_name
    )
    original_filename = save_uploaded_file_as_local_temp_file(original_file)

    return original_filename


def verify_and_return_uploaded_wa_event_file(
    interface: abstractInterface, file_marker_name: str
):
    file = get_file_from_interface(file_marker_name, interface=interface)
    file_ext = os.path.splitext(file.filename)[1]
    if file_ext not in ALLOWED_UPLOAD_FILE_TYPES:
        raise FileError(
            "Not one of file types %s, upload a different file or "
            % ALLOWED_UPLOAD_FILE_TYPES
        )

    return file


TEMP_FILE_NAME = "tempfile"  ## can be anything


def save_uploaded_file_as_local_temp_file(file) -> str:
    new_filename = get_next_valid_upload_file_name(TEMP_FILE_NAME)
    try:
        file.save(new_filename)
    except Exception as e:
        raise FileError(
            "Issue %s saving to filename %s- *CONTACT SUPPORT*" % (str(e), new_filename)
        )

    return new_filename


def load_spreadsheet_file_and_clear_nans(filename: str) -> pd.DataFrame:
    wa_as_df = load_spreadsheet_file(filename)
    wa_as_df = wa_as_df.fillna("")

    return wa_as_df


def get_staged_adhoc_filename(adhoc_name: str):
    return os.path.join(upload_directory, "_%s" % adhoc_name)
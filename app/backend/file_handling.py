import os

import pandas as pd
import qrcode

from app.data_access.init_directories import upload_directory, web_pathname_of_file, download_directory
from app.data_access.configuration.configuration import ALLOWED_UPLOAD_FILE_TYPES
from app.data_access.uploads_and_downloads import get_next_valid_upload_file_name
from app.data_access.xls_and_csv import load_spreadsheet_file
from app.objects.abstract_objects.abstract_form import File
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    get_file_from_interface,
)
from app.objects.exceptions import FileError, arg_not_passed


def create_local_file_from_uploaded_and_return_filename(
    interface: abstractInterface, file_marker_name: str, new_filename: str = arg_not_passed
) -> str:
    file_object = get_file_from_interface_verify_extension_and_return_file_object(
        interface=interface, file_marker_name=file_marker_name
    )
    new_filename = save_uploaded_file_as_local_temp_file(file_object, new_filename=new_filename)

    return new_filename


def get_file_from_interface_verify_extension_and_return_file_object(
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


def save_uploaded_file_as_local_temp_file(file_object, new_filename: str = arg_not_passed) -> str:
    if new_filename is arg_not_passed:
        new_filename = get_next_valid_upload_file_name(TEMP_FILE_NAME)
    try:
        file_object.save(new_filename)
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


def generate_qr_code_for_file_in_public_path(filename:str) -> File:
    web_path = web_pathname_of_file(filename)
    img = qrcode.make(web_path)
    qr_code_filename = temp_qr_code_file_name(filename)
    with open(qr_code_filename, "wb") as qr:
        img.save(qr)

    return File(qr_code_filename)


def temp_qr_code_file_name(filename: str) -> str:
    return os.path.join(download_directory, "temp_qr_code_%s.png" % filename)

import os
import shutil

import pandas as pd
from app.data_access.configuration.configuration import (
    WILD_APRICOT_EVENT_ID,
    WILD_APRICOT_FILE_TYPES,
)
from app.data_access.uploads_and_downloads import (
    staging_directory,
    get_next_valid_upload_file_name,
)
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    get_file_from_interface,
)
from app.backend.wa_import.load_wa_file import WA_FILE
from app.objects.constants import NoValidFile, NoValidID, FileError


def load_raw_wa_file(wa_filename: str) -> pd.DataFrame:
    wa_as_df = load_raw_wa_file_from_spreadsheet(wa_filename)
    wa_as_df = wa_as_df.fillna("")

    return wa_as_df


def load_raw_wa_file_from_spreadsheet(wa_filename: str) -> pd.DataFrame:
    engine_types = ["csv", "xlrd"]
    error_str = (
        "Filename %s is not as expected- are you sure this is a WA export file? Errors: "
        % wa_filename
    )
    for engine in engine_types:
        try:
            if engine == "csv":
                wa_as_df = pd.read_csv(wa_filename, parse_dates=True)
            else:
                wa_as_df = pd.read_excel(wa_filename, engine=engine, parse_dates=True)
            return wa_as_df
        except Exception as e:
            error = "Error %s using engine %s. " % (str(e), engine)
            error_str += error

    raise NoValidFile(error_str)


def get_event_id_from_wa_df(wa_as_df: pd.DataFrame) -> str:
    try:
        series_of_id = wa_as_df[WILD_APRICOT_EVENT_ID]
    except KeyError:
        raise NoValidID(
            "Expected to find field %s in WA file, eithier is not a WA file or WA have changed their column names and configuration needs updating"
            % WILD_APRICOT_EVENT_ID
        )

    unique_id = series_of_id[0]
    all_id_match_in_file = all([id == unique_id for id in series_of_id])

    if not all_id_match_in_file:
        raise NoValidID(
            "Column %s in WA file does not contain identical event IDs"
            % WILD_APRICOT_EVENT_ID
        )
    return str(unique_id)


def does_raw_event_file_exist(event_id: str):
    try:
        filename = get_staged_file_raw_event_filename(event_id)
        with open(filename, "rb") as f:
            pass
        return True
    except:
        return False


def delete_raw_event_upload_with_event_id(event_id: str):
    filename = get_staged_file_raw_event_filename(event_id)
    try:
        os.remove(filename)
    except:
        pass


def save_staged_file_of_raw_event_upload_with_event_id(
    original_filename: str, event_id: str
):
    print(original_filename)
    new_filename = get_staged_file_raw_event_filename(event_id)
    shutil.copy(original_filename, new_filename)


def get_staged_file_raw_event_filename(event_id: str):
    return os.path.join(staging_directory, "raw_event_%s" % event_id)


def verify_and_return_uploaded_wa_event_file(interface: abstractInterface):
    file = get_file_from_interface(WA_FILE, interface=interface)
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

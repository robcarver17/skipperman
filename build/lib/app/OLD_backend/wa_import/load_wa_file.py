import os
import shutil

import pandas as pd

from app.backend.file_handling import load_spreadsheet_file_and_clear_nans
from app.data_access.configuration.configuration import (
    WILD_APRICOT_EVENT_ID,
)
from app.data_access.file_access import upload_directory
from app.objects.exceptions import NoValidID, FileError


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
    return os.path.join(upload_directory, "raw_event_%s" % event_id)




def check_local_file_is_valid_wa_file(new_filename: str):
    ## check can load as a WA file
    try:
        wa_df = load_spreadsheet_file_and_clear_nans(new_filename)
        get_event_id_from_wa_df(wa_df)
    except Exception as e:
        raise FileError("File is not a valid WA event file, error %s" % str(e))


WA_FILE = "file"

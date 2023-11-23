import os
import shutil

import pandas as pd
from app.data_access.configuration.configuration import WILD_APRICOT_EVENT_ID
from app.data_access.uploads_and_downloads import staging_directory
from app.objects.constants import NoValidFile, NoValidID


def load_raw_wa_file(wa_filename: str) -> pd.DataFrame:
    wa_as_df = load_raw_wa_file_from_spreadsheet(wa_filename)
    wa_as_df = wa_as_df.fillna("")

    return wa_as_df

def load_raw_wa_file_from_spreadsheet(wa_filename: str) -> pd.DataFrame:
    engine_types = ['csv', 'xlrd', 'openpyxl', 'odf', 'pyxlsb']
    error_str = "Filename %s is not as expected- are you sure this is a WA export file? Errors: " % wa_filename
    for engine in engine_types:
        try:
            if engine=="csv":
                wa_as_df = pd.read_csv(wa_filename)
            else:
                wa_as_df = pd.read_excel(wa_filename, engine=engine)
            return wa_as_df
        except Exception as e:
            error = "Error %s using engine %s. " % (str(e), engine)
            error_str+=error

    raise NoValidFile(
        error_str
    )



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
    return unique_id


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


def save_staged_file_of_raw_event_upload_with_event_id(original_filename: str, event_id: str):
    print(original_filename)
    new_filename = get_staged_file_raw_event_filename(event_id)
    shutil.copy(original_filename, new_filename)


def get_staged_file_raw_event_filename(event_id: str):
    return os.path.join(staging_directory, "raw_event_%s" % event_id)


import pandas as pd
import numpy as np
from logic.data_and_interface import DataAndInterface


def choose_and_load_raw_wa_file(data_and_interface: DataAndInterface) -> pd.DataFrame:
    interface = data_and_interface.interface

    wa_filename = interface.select_file("Select raw WA file to upload")

    try:
        wa_as_df = load_raw_wa_file(wa_filename)
    except:
        interface.message(
            "%s is not a readable .csv or .xls file; maybe try loading .xls and saving as .csv"
            % wa_filename
        )
        return NO_VALID_FILE

    return wa_as_df


def load_raw_wa_file(wa_filename) -> pd.DataFrame:
    try:
        wa_as_df = pd.read_excel(wa_filename)
    except:
        wa_as_df = pd.read_csv(wa_filename)

    wa_as_df = wa_as_df.fillna("")

    return wa_as_df


NO_VALID_FILE = pd.DataFrame(["not valid file"])
WA_EVENT_ID_FIELD = "Event ID"
NO_VALID_ID = "No valid ID"


def get_event_id_from_wa_df(
    wa_as_df: pd.DataFrame, data_and_interface: DataAndInterface
) -> str:
    interface = data_and_interface.interface

    try:
        series_of_id = wa_as_df[WA_EVENT_ID_FIELD]
    except KeyError:
        interface.message(
            "Expected to find a column called %s in WA file - eithier not a WA file or WA have changed their format"
            % (WA_EVENT_ID_FIELD)
        )
        return NO_VALID_ID

    unique_id = series_of_id[0]
    all_id_match_in_file = all([id == unique_id for id in series_of_id])

    if not all_id_match_in_file:
        interface.message(
            "Column labelled %s in WA value does not contain all identical values - probably not a WA file"
            % (WA_EVENT_ID_FIELD)
        )
        return NO_VALID_ID

    return unique_id

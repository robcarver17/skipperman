from datetime import datetime
from typing import Dict

import pandas as pd

from app.objects.utilities.exceptions import NoValidFile

"""
"""


def load_spreadsheet_file(filename: str) -> pd.DataFrame:
    engine_types = ["csv", "xlrd"]
    error_str = (
        "Filename %s is not as expected- are you sure this is a valid spreadsheet file? Errors: "
        % filename
    )
    for engine in engine_types:
        try:
            if engine == "csv":
                wa_as_df = pd.read_csv(filename, parse_dates=True)
            else:
                wa_as_df = pd.read_excel(filename, engine=engine, parse_dates=True)
            return wa_as_df
        except Exception as e:
            error = "Error %s using engine %s. " % (str(e), engine)
            error_str += error

    raise NoValidFile(error_str)


def save_dict_of_df_as_spreadsheet_file(
    dict_of_df: Dict[str, pd.DataFrame],
    path_and_filename_no_extension: str,
    write_index: bool = False,
):
    try:
        path_and_filename_with_extension = save_dict_of_df_as_xls(
            dict_of_df, path_and_filename_no_extension, write_index=write_index
        )
    except:
        path_and_filename_with_extension = save_dict_of_df_as_csv(
            dict_of_df, path_and_filename_no_extension, write_index=write_index
        )

    return path_and_filename_with_extension


def save_dict_of_df_as_xls(
    dict_of_df: Dict[str, pd.DataFrame],
    path_and_filename_without_extension: str,
    write_index: bool = False,
):
    path_and_filename_with_extension = path_and_filename_without_extension + ".xlsx"
    with pd.ExcelWriter(path_and_filename_with_extension) as writer:
        for sheet_name, df in dict_of_df.items():
            full_sheet_name = "%s Printed %s" % (sheet_name, datetime.now().strftime("%b %d %H%M"))
            df.to_excel(writer, sheet_name=full_sheet_name, index=write_index)

    return path_and_filename_with_extension


def save_dict_of_df_as_csv(
    dict_of_df: Dict[str, pd.DataFrame],
    path_and_filename_without_extension: str,
    write_index: bool = False,
):
    path_and_filename_with_extension = path_and_filename_without_extension + ".csv"
    with open(path_and_filename_with_extension, "a") as f:
        for sheet_name, df in dict_of_df.items():
            f.write(sheet_name)
            df.to_csv(f, index=write_index)
            f.write("\n")

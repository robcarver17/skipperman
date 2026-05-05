from copy import copy
from datetime import datetime
from typing import Dict

import pandas as pd

from app.data_access.configuration.configuration import local_timezone
from app.data_access.file_access import PathAndFilename
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
                #wa_as_df = pd.read_csv(filename, parse_dates=True, date_format='%m/%d/%Y %H:%M:%S')
                wa_as_df = pd.read_csv(filename, parse_dates=True)
            else:
                #wa_as_df = pd.read_excel(filename, engine=engine, parse_dates=True, date_format='%d/%m/%Y %H:%M:%S')
                wa_as_df = pd.read_excel(filename, engine=engine, parse_dates=True)
            return wa_as_df
        except Exception as e:
            error = "Error importing file %s using engine %s python version for pandas is %s" % (str(e), engine, pd.__version__)
            error_str += error

    raise NoValidFile(error_str)


def save_dict_of_df_as_spreadsheet_file(
    dict_of_df: Dict[str, pd.DataFrame],
    path_and_filename_no_extension: PathAndFilename,
    write_index: bool = False,
    header_str: str = "",
) -> PathAndFilename:
    try:
        path_and_filename_with_extension = save_dict_of_df_as_xls(
            dict_of_df,
            path_and_filename_no_extension,
            write_index=write_index,
            header_str=header_str,
        )
    except Exception as e:
        print("")
        print("************")
        print("Error output spreadsheet %s" % str(e))
        print("************")
        print("")
        path_and_filename_with_extension = save_dict_of_df_as_csv(
            dict_of_df, path_and_filename_no_extension, write_index=write_index
        )

    return path_and_filename_with_extension


def save_dict_of_df_as_xls(
    dict_of_df: Dict[str, pd.DataFrame],
    path_and_filename_without_extension: PathAndFilename,
    write_index: bool = False,
    header_str: str = "",
) -> PathAndFilename:
    path_and_filename = copy(path_and_filename_without_extension)
    path_and_filename.add_or_replace_extension(".xlsx")
    with pd.ExcelWriter(path_and_filename.full_path_and_name) as writer:
        for sheet_name, df in dict_of_df.items():
            full_sheet_name = "%s Printed %s %s" % (
                sheet_name,
                datetime.now(local_timezone).strftime("%b %d %H%M"),
                header_str,
            )
            full_sheet_name = full_sheet_name[:31]
            df.to_excel(writer, sheet_name=full_sheet_name, index=write_index)

    return path_and_filename


def save_dict_of_df_as_csv(
    dict_of_df: Dict[str, pd.DataFrame],
    path_and_filename_without_extension: PathAndFilename,
    write_index: bool = False,
) -> PathAndFilename:
    path_and_filename = copy(path_and_filename_without_extension)
    path_and_filename.add_or_replace_extension(".csv")
    with open(path_and_filename.full_path_and_name, "a") as f:
        for sheet_name, df in dict_of_df.items():
            f.write(sheet_name)
            df.to_csv(f, index=write_index)
            f.write("\n")

    return path_and_filename


SPREADSHEET_FILE_EXTENSIONS = [".csv", ".xlsx"]


def load_spreadsheet_file_and_clear_nans(filename: str) -> pd.DataFrame:
    wa_as_df = load_spreadsheet_file(filename)
    wa_as_df = wa_as_df.fillna("")

    return wa_as_df

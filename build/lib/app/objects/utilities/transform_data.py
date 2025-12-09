import datetime
import math
from typing import Dict, Union, List

import pandas as pd
from dateutil.parser import parse

from app.data_access.configuration.field_list_groups import FIELDS_AS_STR, FIELDS_WITH_DATES, FIELDS_WITH_DATETIMES
from app.data_access.configuration.fixed import ID_KEY, ID_KEY_SUFFIX, LIST_OF_ID_KEY_TO_IGNORE_WHEN_CLEANING
from app.objects.utilities.utils import in_both_x_and_y


def clean_up_dict_with_nans(some_dict) -> dict:
    for key, value in some_dict.items():
        try:
            if math.isnan(value):
                some_dict[key] = ""
        except:
            ## another type
            pass
    return some_dict


def clean_up_dict_with_weird_floats_for_id(some_dict) -> dict:
    for key, value in some_dict.items():
        key_is_id = key == ID_KEY
        key_contains_id = ID_KEY_SUFFIX in key
        key_is_row_id = (
            key in LIST_OF_ID_KEY_TO_IGNORE_WHEN_CLEANING
        )  ## special event row id, FIXME orrible hack
        if key_is_row_id:
            continue
        elif key_is_id or key_contains_id:
            some_dict[key] = make_id_as_int_str(value)

    return some_dict


def make_id_as_int_str(value: str) -> str:
    try:
        return str(int(float(value)))
    except:
        ## actually a string
        return value


KEY_VALUE_SEPERATOR = ":"
ITEM_SEPERATOR = ","
LIST_SEPERATOR = "_"

def list_from_str(object_as_str: str, type_to_use = int):
    list_of_values = object_as_str.split(LIST_SEPERATOR)
    list_of_values= [type_to_use(value) for value in list_of_values]

    return list_of_values

def str_from_list(some_list: List):
    list_of_str = [str(value) for value in some_list]
    return LIST_SEPERATOR.join(list_of_str)

def dict_from_str(object_as_str: str) -> dict:
    as_list_of_str = object_as_str.split(ITEM_SEPERATOR)
    as_list_of_key_value_pairs = [
        key_value_as_str.split(KEY_VALUE_SEPERATOR)
        for key_value_as_str in as_list_of_str
    ]
    as_dict = dict([(key, value) for key, value in as_list_of_key_value_pairs])

    return as_dict


def dict_as_str(some_dict: Dict[str, str]) -> str:
    as_list_of_str = [
        "%s%s%s" % (key, KEY_VALUE_SEPERATOR, value) for key, value in some_dict.items()
    ]

    return ITEM_SEPERATOR.join(as_list_of_str)


def transform_df_to_str(df: pd.DataFrame):
    for field in df.columns:
        if field in FIELDS_AS_STR:
            df[field] = df[field].astype(str)

    return df


def transform_df_from_dates_to_str(df: pd.DataFrame):
    field_with_dates = in_both_x_and_y(list(df.columns), FIELDS_WITH_DATES)
    field_with_datetimes = in_both_x_and_y(list(df.columns), FIELDS_WITH_DATETIMES)

    for field in field_with_dates:
        transform_df_column_from_dates_to_str(df=df, date_series_name=field)
    for field in field_with_datetimes:
        transform_df_column_from_datetime_to_str(df=df, date_series_name=field)


def transform_df_column_from_dates_to_str(df: pd.DataFrame, date_series_name: str):
    date_series = getattr(df, date_series_name)
    date_series = [transform_date_into_str(date) for date in date_series]
    setattr(df, date_series_name, date_series)


def transform_date_into_str(date: datetime.date) -> str:
    return date.strftime(DATE_STR)


def transform_df_column_from_datetime_to_str(df: pd.DataFrame, date_series_name: str):
    date_series = getattr(df, date_series_name)
    date_series = [transform_datetime_into_str(date) for date in date_series]
    setattr(df, date_series_name, date_series)


def transform_datetime_into_str(date: datetime.datetime) -> str:
    return date.strftime(DATETIME_STR)


def transform_df_from_str_to_dates(df: pd.DataFrame):
    if len(df) == 0:
        return df
    fields_with_dates = in_both_x_and_y(list(df.columns), FIELDS_WITH_DATES)
    fields_with_datetimes = in_both_x_and_y(list(df.columns), FIELDS_WITH_DATETIMES)
    for date_series_name in fields_with_dates:
        transform_df_column_from_str_to_dates(df=df, date_series_name=date_series_name)
    for field in fields_with_datetimes:
        transform_df_column_from_str_to_datetimes(df=df, date_series_name=field)


def transform_df_column_from_str_to_dates(df: pd.DataFrame, date_series_name: str):
    date_series = getattr(df, date_series_name)
    date_series = [
        transform_str_or_datetime_into_date(date_str) for date_str in date_series
    ]
    setattr(df, date_series_name, date_series)


def transform_str_or_datetime_into_date(
    date_string: Union[str, datetime.date, datetime.datetime]
) -> datetime.date:
    if isinstance(date_string, datetime.date):
        return date_string
    elif isinstance(date_string, datetime.datetime):
        return date_string.date()

    return transform_str_into_date(date_string)


def transform_str_into_date(date_string: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(date_string, DATE_STR).date()
    except:
        pass

    try:
        return transform_str_into_datetime(date_string)
    except:
        pass

    return datetime.datetime(1970, 1, 1)


def transform_df_column_from_str_to_datetimes(df: pd.DataFrame, date_series_name: str):
    date_series = getattr(df, date_series_name)
    date_series = [transform_str_into_datetime(date_str) for date_str in date_series]
    setattr(df, date_series_name, date_series)


def transform_str_into_datetime(date_string: str) -> datetime.datetime:
    if isinstance(date_string, datetime.datetime):
        return date_string

    try:
        return datetime.datetime.strptime(date_string, DATETIME_STR)
    except:
        return parse(date_string)


DATE_STR = "%Y/%m/%d"
DATETIME_STR = "%Y/%m/%d %H:%M:%S.%f"


def dict_as_single_str(some_dict: dict) -> str:
    single_list = ["%s:%s" % (key, value) for key, value in some_dict.items()]
    return ",".join(single_list)


def from_single_str_to_dict(single_str: str) -> dict:
    entries = single_str.split(",")
    output_dict = dict([entry.split(":") for entry in entries])
    return output_dict


TRUE = "TRUE_VALUE"
FALSE = "FALSE_VALUE"


def from_bool_to_str(class_instance: bool) -> str:
    if class_instance:
        return TRUE
    else:
        return FALSE


def from_str_to_bool(string: str) -> bool:
    return string == TRUE

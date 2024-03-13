from collections import defaultdict
import datetime
import math
from dataclasses import dataclass

import pandas as pd
from difflib import SequenceMatcher

from app.data_access.configuration.field_list_groups import FIELDS_WITH_DATES, FIELDS_WITH_DATETIMES, FIELDS_AS_STR
from dateutil.parser import parse


def data_object_as_dict(some_object) -> dict:
    list_of_attributes = get_list_of_attributes(some_object)

    object_as_dict = dict(
        [(key, getattr(some_object, key)) for key in list_of_attributes]
    )

    return object_as_dict


def create_list_of_objects_from_dataframe(class_of_object, df: pd.DataFrame):
    list_of_objects = [
        create_object_from_df_row(class_of_object=class_of_object, row=row)
        for index, row in df.iterrows()
    ]

    return list_of_objects


def create_object_from_df_row(class_of_object, row: pd.Series):
    row_as_dict = row.to_dict()

    try:
        object = class_of_object.from_dict(row_as_dict)
    except:
        raise Exception(
            _error_str_when_creating_object_from_df_row(
                class_of_object=class_of_object, row_as_dict=dict(row_as_dict)
            )
        )

    return object


def _error_str_when_creating_object_from_df_row(class_of_object, row_as_dict: dict):
    if getattr(class_of_object, "from_dict", None) is None:
        return Exception(
            "Class %s requires .from_dict() method" % (str(class_of_object))
        )
    list_of_attributes = get_list_of_attributes(some_class=class_of_object)
    return Exception(
        "Class %s requires elements %s element %s doesn't match"
        % (str(class_of_object), str(list_of_attributes), str(row_as_dict))
    )


def get_list_of_attributes(some_class) -> list:
    dict_of_attributes = get_dict_of_class_attributes(some_class)
    return list(dict_of_attributes.keys())


def get_dict_of_class_attributes(some_class) -> dict:
    return some_class.__annotations__


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


@dataclass
class SingleDiff:
    old_value: object
    new_value: object


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
        if key == "id":
            some_dict[key] = make_id_as_int_str(value)

    return some_dict

def make_id_as_int_str(value: str)->str:
    return str(int(float(value)))

def list_duplicate_indices(seq):
    tally = defaultdict(list)
    for i, item in enumerate(seq):
        tally[item].append(i)
    return [locs for locs in tally.values() if len(locs) > 1]


def transform_df_to_str(df: pd.DataFrame):
    for field in df.columns:
        if field in FIELDS_AS_STR:
            df[field] = df[field].astype(str)

    return df


def transform_df_from_dates_to_str(df: pd.DataFrame):
    for field in FIELDS_WITH_DATES:
        transform_df_column_from_dates_to_str(df=df, date_series_name=field)
    for field in FIELDS_WITH_DATETIMES:
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
    for field in FIELDS_WITH_DATES:
        transform_df_column_from_str_to_dates(df=df, date_series_name=field)
    for field in FIELDS_WITH_DATETIMES:
        transform_df_column_from_str_to_datetimes(df=df, date_series_name=field)


def transform_df_column_from_str_to_dates(df: pd.DataFrame, date_series_name: str):
    date_series = getattr(df, date_series_name)
    date_series = [transform_str_into_date(date_str) for date_str in date_series]
    setattr(df, date_series_name, date_series)


def transform_str_into_date(date_string: str) -> datetime.date:
    if isinstance(date_string, datetime.date):
        return date_string
    elif isinstance(date_string, datetime.datetime):
        return date_string.date()

    try:
        return datetime.datetime.strptime(date_string, DATE_STR).date()
    except:
        str_as_datetime = transform_str_into_datetime(date_string)
        return str_as_datetime.date()


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


def in_x_not_in_y(x: list,y: list) -> list:
    return list(set(x).difference(set(y)))


def in_both_x_and_y(x: list,y: list) -> list:
    return list(set(x).intersection(set(y)))

def union_of_x_and_y(x: list,y: list) -> list:
    return list(set(x).union(set(y)))

DATE_STR = "%Y/%m/%d"
DATETIME_STR = "%Y/%m/%d %H:%M:%S.%f"


def dict_as_single_str(some_dict: dict) -> str:
    single_list = ["%s:%s" % (key, value) for key, value in some_dict.items()]
    return ",".join(single_list)


def from_single_str_to_dict(single_str: str)->dict:
    entries = single_str.split(",")
    output_dict = dict([
        entry.split(":") for entry in entries
    ])
    return output_dict

import pandas as pd
import datetime
from app.objects.field_list import FIELDS_WITH_DATES, FIELDS_WITH_DATETIMES

DATE_STR = "%Y/%m/%d"
DATETIME_STR = "%Y/%m/%d %H:%M:%S.%f"


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
    return datetime.datetime.strptime(date_string, DATE_STR).date()


def transform_df_column_from_str_to_datetimes(df: pd.DataFrame, date_series_name: str):
    date_series = getattr(df, date_series_name)
    date_series = [transform_str_into_datetime(date_str) for date_str in date_series]
    setattr(df, date_series_name, date_series)


def transform_str_into_datetime(date_string: str) -> datetime.datetime:
    return datetime.datetime.strptime(date_string, DATETIME_STR)

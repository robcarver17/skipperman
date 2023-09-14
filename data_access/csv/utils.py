import pandas as pd
import datetime


def transform_df_column_from_dates_to_str(
    df: pd.DataFrame, date_series_name: str
) -> pd.DataFrame:
    date_series = getattr(df, date_series_name)
    date_series = [transform_str_from_date(date) for date in date_series]
    setattr(df, date_series_name, date_series)

    return df


def transform_df_column_from_str_to_dates(
    df: pd.DataFrame, date_series_name: str
) -> pd.DataFrame:
    date_series = getattr(df, date_series_name)
    date_series = [transform_date_from_str(date_str) for date_str in date_series]
    setattr(df, date_series_name, date_series)

    return df

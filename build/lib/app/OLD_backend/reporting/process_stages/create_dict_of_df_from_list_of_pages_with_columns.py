from typing import Dict, Tuple

import pandas as pd

from app.OLD_backend.reporting.process_stages.strings_columns_groups import (
    ListOfPagesWithColumns,
    PageWithColumns,
    Column,
    GroupOfMarkedUpString,
)


def convert_list_of_pages_with_columns_to_dict_of_df(
    list_of_pages_with_columns: ListOfPagesWithColumns,
) -> Dict[str, pd.DataFrame]:
    dict_of_df = {}
    for page in list_of_pages_with_columns:
        df_name, df = convert_page_into_named_df(page)
        dict_of_df[df_name] = df

    return dict_of_df


def convert_page_into_named_df(page: PageWithColumns) -> Tuple[str, pd.DataFrame]:
    df = pd.DataFrame()
    for column in page:
        df_for_column = convert_column_into_df(column)
        df = pd.concat([df, df_for_column], axis=0)

    return page.title_str, df


def convert_column_into_df(column: Column) -> pd.DataFrame:
    df_for_column = pd.DataFrame()
    for group_of_marked_string in column:
        df_for_group = convert_group_of_marked_str_into_df(group_of_marked_string)
        df_for_column = pd.concat([df_for_column, df_for_group], axis=0)

    return df_for_column


def convert_group_of_marked_str_into_df(
    group_of_marked_string: GroupOfMarkedUpString,
) -> pd.DataFrame:
    list_of_df = []
    for marked_str in group_of_marked_string:
        series = marked_str.original_contents_as_series
        list_of_df.append(series)

    df = pd.DataFrame(list_of_df)

    return df

from typing import List, Dict
import pandas as pd

from app.backend.reporting.arrangement.group_order import GroupOrder
from app.backend.reporting.options_and_parameters.marked_up_list_from_df_parameters import \
    MarkedUpListFromDfParametersWithActualGroupOrder

from app.backend.reporting.process_stages.strings_columns_groups import (
    GroupOfMarkedUpString,
    MarkedUpString, Page, ListOfPages,
)
from app.objects.constants import arg_not_passed


def create_list_of_pages_from_dict_of_df(
    dict_of_df: Dict[str, pd.DataFrame],
    marked_up_list_from_df_parameters: MarkedUpListFromDfParametersWithActualGroupOrder,
) -> ListOfPages:

    ordered_list_of_groups = marked_up_list_from_df_parameters.actual_group_order
    dict_of_grouped_df = get_dict_of_grouped_df(
        dict_of_df=dict_of_df, marked_up_list_from_df_parameters=marked_up_list_from_df_parameters
    )

    list_of_pages = [create_page_from_df(grouped_df=grouped_df,
                                         ordered_list_of_groups=ordered_list_of_groups,
                                         marked_up_list_from_df_parameters=marked_up_list_from_df_parameters,
                                         title_str=key)
                     for key, grouped_df in dict_of_grouped_df.items()]

    return ListOfPages(list_of_pages)


def create_page_from_df(grouped_df: pd.core.groupby.generic.DataFrameGroupBy,
                        ordered_list_of_groups: GroupOrder,
                        marked_up_list_from_df_parameters: MarkedUpListFromDfParametersWithActualGroupOrder,
                        title_str: str)-> Page:
    page = Page([], title_str=title_str)
    for group in ordered_list_of_groups:
        group_of_marked_up_str = _create_marked_up_str_for_group(
            group=group,
            grouped_df=grouped_df,
            marked_up_list_from_df_parameters=marked_up_list_from_df_parameters,
        )
        page.append(group_of_marked_up_str)

    return page


def get_dict_of_grouped_df(
    dict_of_df: Dict[str, pd.DataFrame],
    marked_up_list_from_df_parameters: MarkedUpListFromDfParametersWithActualGroupOrder,
) -> Dict[str, pd.core.groupby.generic.DataFrameGroupBy]:
    group_by_column = marked_up_list_from_df_parameters.group_by_column
    if group_by_column is arg_not_passed:
        return dict_of_df

    dict_of_grouped_df = dict([
                            (key,
                             get_grouped_df(df=df,
                                         group_by_column =group_by_column ))
                               for key, df in dict_of_df.items()])

    return dict_of_grouped_df

def get_grouped_df(
    df: pd.DataFrame,
    group_by_column: str
) -> pd.core.groupby.generic.DataFrameGroupBy:

    grouped_df = df.groupby(group_by_column )

    return grouped_df


def _create_marked_up_str_for_group(
    group: str,
    grouped_df: pd.core.groupby.generic.DataFrameGroupBy,
    marked_up_list_from_df_parameters: MarkedUpListFromDfParametersWithActualGroupOrder,
) -> GroupOfMarkedUpString:

    subset_group = grouped_df.get_group(group)
    subset_group_as_list = list(subset_group.iterrows())

    if len(subset_group_as_list)==0:
        return GroupOfMarkedUpString([])

    group_of_marked_up_str = GroupOfMarkedUpString()
    _add_groupname_inplace_to_list_for_this_group_if_required(
        group=group,
        group_of_marked_up_str=group_of_marked_up_str,
        marked_up_list_from_df_parameters=marked_up_list_from_df_parameters,
    )

    for index, row in enumerate(subset_group_as_list):
        __, row_entries = row
        prepend_group_name = marked_up_list_from_df_parameters.prepend_group_name
        keyvalue = (
            marked_up_list_from_df_parameters.first_value_in_group_is_key and index == 0
        )
        marked_string = create_marked_string_from_row(
            row_entries,
            entry_columns=marked_up_list_from_df_parameters.entry_columns,
            keyvalue=keyvalue,
            prepend_group_name=prepend_group_name,
            group=group,
        )
        group_of_marked_up_str.append(marked_string)

    return group_of_marked_up_str


def _add_groupname_inplace_to_list_for_this_group_if_required(
    group: str,
    group_of_marked_up_str: GroupOfMarkedUpString,
    marked_up_list_from_df_parameters: MarkedUpListFromDfParametersWithActualGroupOrder,
):
    if marked_up_list_from_df_parameters.include_group_as_header:
        group_of_marked_up_str.append(MarkedUpString.header(group))


def create_marked_string_from_row(
    row: pd.Series,
    entry_columns: List[str],
    group: str,
    keyvalue: bool = False,
    prepend_group_name: bool = False,
) -> MarkedUpString:
    entry = " ".join([row[column_name] for column_name in entry_columns])
    if prepend_group_name:
        entry = "%s: %s" % (group, entry)
    if keyvalue:
        return MarkedUpString.keyvalue(entry)
    else:
        return MarkedUpString.bodytext(entry)

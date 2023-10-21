from typing import List
import pandas as pd

from app.interface import (
    ReportingOptionsForSpecificGroupsInReport,
    MarkedUpListFromDfParametersWithActualGroupOrder,
)

from app.interface import (
    ListOfGroupsOfMarkedUpStrings,
    GroupOfMarkedUpString,
    MarkedUpString,
)


def create_list_of_group_of_marked_up_str_from_df(
    df: pd.DataFrame, report_options: ReportingOptionsForSpecificGroupsInReport
) -> ListOfGroupsOfMarkedUpStrings:

    marked_up_list_from_df_parameters = report_options.marked_up_list_from_df
    ordered_list_of_groups = marked_up_list_from_df_parameters.actual_group_order
    grouped_df = df.groupby(marked_up_list_from_df_parameters.group_by_column)

    list_of_groups_of_marked_up_str = ListOfGroupsOfMarkedUpStrings()
    for group in ordered_list_of_groups:
        group_of_marked_up_str = _create_marked_up_str_for_group(
            group=group,
            grouped_df=grouped_df,
            marked_up_list_from_df_parameters=marked_up_list_from_df_parameters,
        )
        list_of_groups_of_marked_up_str.append(group_of_marked_up_str)

    return list_of_groups_of_marked_up_str


def _create_marked_up_str_for_group(
    group: str,
    grouped_df: pd.core.groupby.generic.DataFrameGroupBy,
    marked_up_list_from_df_parameters: MarkedUpListFromDfParametersWithActualGroupOrder,
) -> GroupOfMarkedUpString:

    subset_group = grouped_df.get_group(group)
    subset_group_as_list = list(subset_group.iterrows())

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

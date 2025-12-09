from typing import Dict
import pandas as pd

from app.backend.reporting import ReportingOptions
from app.backend.reporting.arrangement.group_order import GroupOrder
from app.backend.reporting.options_and_parameters.marked_up_list_from_df_parameters import (
    MarkedUpListFromDfParametersWithActualGroupOrder,
)

from app.backend.reporting.process_stages.strings_columns_groups import (
    GroupOfMarkedUpString,
    MarkedUpString,
    Page,
    ListOfPages,
    EMPTY_GROUP,
)
from app.objects.utilities.exceptions import arg_not_passed


class ListOfDfRowsFromSubset(list):
    @property
    def columns(self):
        if len(self) == 0:
            return []
        return list(self[0][1].keys())


def create_list_of_pages_from_dict_of_df(
    dict_of_df: Dict[str, pd.DataFrame],
        reporting_options: ReportingOptions
,
) -> ListOfPages:
    marked_up_list_from_df_parameters = reporting_options.marked_up_list_from_df_parameters ## ignore
    ordered_list_of_groups = marked_up_list_from_df_parameters.actual_group_order
    dict_of_grouped_df = get_dict_of_grouped_df(
        dict_of_df=dict_of_df,
        marked_up_list_from_df_parameters=marked_up_list_from_df_parameters,
    )

    list_of_pages = [
        create_page_from_df(
            grouped_df=grouped_df,
            ordered_list_of_groups=ordered_list_of_groups,
            marked_up_list_from_df_parameters=marked_up_list_from_df_parameters,
            page_name=page_name
        )
        for page_name, grouped_df in dict_of_grouped_df.items()
    ]

    return ListOfPages(list_of_pages)


def create_page_from_df(
    grouped_df: pd.core.groupby.generic.DataFrameGroupBy,
        page_name: str,
    ordered_list_of_groups: GroupOrder,
    marked_up_list_from_df_parameters: MarkedUpListFromDfParametersWithActualGroupOrder,
) -> Page:
    page = Page([], title_str=page_name)
    groups_with_content = []
    for group in ordered_list_of_groups:
        group_of_marked_up_str = _create_marked_up_str_for_group(
            group=group,
            grouped_df=grouped_df,
            marked_up_list_from_df_parameters=marked_up_list_from_df_parameters,
           page_name=page_name
        )
        if group_of_marked_up_str is EMPTY_GROUP:
            continue
        else:
            page.append(group_of_marked_up_str)
            groups_with_content.append(group)

    page.group_names = groups_with_content

    return page


def get_dict_of_grouped_df(
    dict_of_df: Dict[str, pd.DataFrame],
    marked_up_list_from_df_parameters: MarkedUpListFromDfParametersWithActualGroupOrder,
) -> Dict[str, pd.core.groupby.generic.DataFrameGroupBy]:
    group_by_column = marked_up_list_from_df_parameters.group_by_column
    if group_by_column is arg_not_passed:
        return dict_of_df

    dict_of_grouped_df = dict(
        [
            (key, get_grouped_df(df=df, group_by_column=group_by_column))
            for key, df in dict_of_df.items()
        ]
    )

    dict_of_grouped_df = dict(
        [
            (key, grouped_df)
            for key, grouped_df in dict_of_grouped_df.items()
            if grouped_df is not EMPTY_DF
        ]
    )

    return dict_of_grouped_df


EMPTY_DF = object()


def get_grouped_df(
    df: pd.DataFrame, group_by_column: str
) -> pd.core.groupby.generic.DataFrameGroupBy:
    if len(df) == 0:
        return EMPTY_DF

    grouped_df = df.groupby(group_by_column)

    return grouped_df


def _create_marked_up_str_for_group(
    group: str,
        page_name: str,
    grouped_df: pd.core.groupby.generic.DataFrameGroupBy,
    marked_up_list_from_df_parameters: MarkedUpListFromDfParametersWithActualGroupOrder,
) -> GroupOfMarkedUpString:
    subset_group_as_list = subset_list_for_group(group=group, grouped_df=grouped_df)

    group_of_marked_up_str = group_of_marked_up_str_from_subset_list_for_group(
        subset_group_as_list=subset_group_as_list,
        marked_up_list_from_df_parameters=marked_up_list_from_df_parameters,
        group=group,page_name=page_name
    )

    return group_of_marked_up_str


def group_of_marked_up_str_from_subset_list_for_group(
    group: str,
        page_name: str,
    subset_group_as_list: ListOfDfRowsFromSubset,
    marked_up_list_from_df_parameters: MarkedUpListFromDfParametersWithActualGroupOrder,
) -> GroupOfMarkedUpString:
    group_of_marked_up_str = GroupOfMarkedUpString()
    if len(subset_group_as_list) == 0:
        return EMPTY_GROUP

    _add_groupname_inplace_to_list_for_this_group_if_required(
        group=group,
        page_name=page_name,
        group_of_marked_up_str=group_of_marked_up_str,
        marked_up_list_from_df_parameters=marked_up_list_from_df_parameters,
        size_of_group=len(subset_group_as_list),
    )
    dict_of_max_length = dict_of_max_length_by_column_name_across_list(
        subset_group_as_list=subset_group_as_list
    )

    prepend_group_name = marked_up_list_from_df_parameters.prepend_group_name
    include_row_count = marked_up_list_from_df_parameters.include_row_count
    group_by_column = marked_up_list_from_df_parameters.group_by_column
    drop_group_name_from_columns = marked_up_list_from_df_parameters.drop_group_name_from_columns

    for index, row in enumerate(subset_group_as_list):
        __, row_entries = row  ## weird pandas thing
        keyvalue = (
            marked_up_list_from_df_parameters.first_value_in_group_is_key and index == 0
        )
        marked_string = create_marked_string_from_row(
            row_entries,
            index=index,
            keyvalue=keyvalue,
            prepend_group_name=prepend_group_name,
            include_row_count=include_row_count,
            group=group,
            dict_of_max_length=dict_of_max_length,
            group_by_column=group_by_column,
            drop_group_name_from_columns=drop_group_name_from_columns
        )
        group_of_marked_up_str.append(marked_string)

    return group_of_marked_up_str


def dict_of_max_length_by_column_name_across_list(
    subset_group_as_list: ListOfDfRowsFromSubset,
) -> Dict[str, int]:
    if len(subset_group_as_list) == 0:
        return {}

    entry_columns = (
        subset_group_as_list.columns
    )  ## should all be the same, joy of itterows
    dict_of_max_length = dict(
        [
            (
                column_name,
                max_length_for_column_name_across_list(
                    subset_group_as_list=subset_group_as_list, column_name=column_name
                ),
            )
            for column_name in entry_columns
        ]
    )

    return dict_of_max_length


def max_length_for_column_name_across_list(
    subset_group_as_list: ListOfDfRowsFromSubset, column_name: str
) -> int:
    max_length = 0
    for index, row in enumerate(subset_group_as_list):
        __, row_entries = row  ## weird pandas thing
        item = row_entries[column_name]
        len_item = len(item)
        if len_item > max_length:
            max_length = len_item

    return max_length


def subset_list_for_group(
    group: str,
    grouped_df: pd.core.groupby.generic.DataFrameGroupBy,
) -> ListOfDfRowsFromSubset:
    try:
        subset_group = grouped_df.get_group(group)
    except KeyError:
        ## possible with multiple pages that not all groups on each page
        return ListOfDfRowsFromSubset()

    subset_group_as_list = ListOfDfRowsFromSubset(subset_group.iterrows())

    return subset_group_as_list


def _add_groupname_inplace_to_list_for_this_group_if_required(
    group: str,
        page_name: str,
        group_of_marked_up_str: GroupOfMarkedUpString,
    marked_up_list_from_df_parameters: MarkedUpListFromDfParametersWithActualGroupOrder,
    size_of_group: int,
):
    if marked_up_list_from_df_parameters.include_group_as_header:
        group_name = group
        if marked_up_list_from_df_parameters.include_size_of_group_if_header:
            group_name = group_name + "(%d)" % size_of_group

        if marked_up_list_from_df_parameters.group_annotations is not arg_not_passed:
            annotation_for_day = marked_up_list_from_df_parameters.group_annotations.get(page_name)
            annotation = annotation_for_day.get(group, "")
            group_name = group_name+" "+annotation

        group_of_marked_up_str.append(MarkedUpString.header(group_name))


def create_marked_string_from_row(
    row: pd.Series,
    group: str,
    index: int,
    dict_of_max_length: Dict[str, int],
        group_by_column: str,
        keyvalue: bool = False,
    prepend_group_name: bool = False,
include_row_count: bool = False,
        drop_group_name_from_columns: bool = False

) -> MarkedUpString:
    if drop_group_name_from_columns:
        row = row.drop(group_by_column)

    if keyvalue:
        return MarkedUpString.keyvalue(
            index=index,
            row=row,
            group=group,
            prepend_group_name=prepend_group_name,
            dict_of_max_length=dict_of_max_length,
            include_row_count=include_row_count
        )
    else:
        return MarkedUpString.bodytext(
            index=index,
            row=row,
            group=group,
            prepend_group_name=prepend_group_name,
            dict_of_max_length=dict_of_max_length,
            include_row_count=include_row_count
        )

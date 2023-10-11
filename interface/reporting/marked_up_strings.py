from copy import copy
from dataclasses import dataclass
from typing import List

import pandas as pd

from objects.constants import arg_not_passed


@dataclass
class MarkedUpString:
    string: str
    italics: bool = False
    bold: bool = False
    underline: bool = False
    large_font: bool = False

    @classmethod
    def bodytext(cls, string):
        return cls(
            string=string, bold=False, italics=False, underline=False, large_font=False
        )

    @classmethod
    def header(cls, string):
        return cls(
            string=string, bold=True, italics=False, underline=True, large_font=False
        )

    @classmethod
    def keyvalue(cls, string):
        return cls(
            string=string, bold=True, italics=False, underline=False, large_font=False
        )

    @classmethod
    def title(cls, string):
        return cls(
            string=string, bold=True, large_font=True, italics=False, underline=False
        )


@dataclass
class MarkedUpListFromDfParameters:
    entry_columns: List[str]
    group_by_column: str
    include_group_as_header: bool = True
    first_value_in_group_is_key: bool = False
    force_group_order: list = arg_not_passed
    prepend_group_name: bool = False

    def set_and_return_list_of_groups(
        self, grouped_df: pd.core.groupby.generic.DataFrameGroupBy
    ) -> list:
        if self.force_group_order is arg_not_passed:
            list_of_groups = list(grouped_df.groups.keys())
        else:
            list_of_groups = self.force_group_order

        return list_of_groups

    @property
    def use_entry_columns(self) -> list:
        if self.prepend_group_name:
            use_entry_columns = copy(self.entry_columns)
            use_entry_columns = [self.group_by_column] + use_entry_columns
            return use_entry_columns
        else:
            return self.entry_columns


def create_nested_list_of_marked_up_str_from_df(
    df: pd.DataFrame, parameters: MarkedUpListFromDfParameters
):

    grouped_df = df.groupby(parameters.group_by_column)
    list_of_groups = parameters.set_and_return_list_of_groups(grouped_df)

    nested_list_of_str = []
    for group in list_of_groups:
        list_for_this_group = _create_list_of_marked_up_str_for_group(
            group=group, grouped_df=grouped_df, parameters=parameters
        )
        nested_list_of_str.append(list_for_this_group)

    return nested_list_of_str


def _create_list_of_marked_up_str_for_group(
    group: str,
    grouped_df: pd.core.groupby.generic.DataFrameGroupBy,
    parameters: MarkedUpListFromDfParameters,
):

    subset_group = grouped_df.get_group(group)
    subset_group_as_list = list(subset_group.iterrows())

    list_for_this_group = []
    _add_groupname_inplace_to_list_for_this_group_if_required(
        group=group, list_for_this_group=list_for_this_group, parameters=parameters
    )

    _add_first_row_inplace_to_list_for_this_group_if_required(
        subset_group_as_list=subset_group_as_list,
        list_for_this_group=list_for_this_group,
        parameters=parameters,
    )

    for __, row in subset_group_as_list:
        marked_string = create_marked_string_from_row(
            row, use_entry_columns=parameters.use_entry_columns
        )
        list_for_this_group.append(marked_string)

    return list_for_this_group


def _add_first_row_inplace_to_list_for_this_group_if_required(
    subset_group_as_list: list,
    list_for_this_group: list,
    parameters: MarkedUpListFromDfParameters,
):
    if parameters.first_value_in_group_is_key:
        first_row = subset_group_as_list.pop(0)[1]
        first_marked_string = create_marked_string_from_row(
            first_row, use_entry_columns=parameters.use_entry_columns, keyvalue=True
        )
        list_for_this_group.append(first_marked_string)


def _add_groupname_inplace_to_list_for_this_group_if_required(
    group: str, list_for_this_group: list, parameters: MarkedUpListFromDfParameters
):

    if parameters.include_group_as_header:
        list_for_this_group.append(MarkedUpString.header(group))


def create_marked_string_from_row(
    row: pd.Series, use_entry_columns: List[str], keyvalue: bool = False
) -> MarkedUpString:

    entry = " ".join([row[column_name] for column_name in use_entry_columns])
    if keyvalue:
        return MarkedUpString.keyvalue(entry)
    else:
        return MarkedUpString.bodytext(entry)


def create_column_pdf_from_list_of_str(nested_list_of_str: list):
    ## Create column pdf from nested_list of strings
    ## Each element of nested list is a group of a list of strings, one per line
    ## We want to print each group as a single block
    pass

from copy import copy
from typing import List, Dict
import pandas as pd
from app.objects.utils import in_x_not_in_y

from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)


class GroupOrder(List[str]):
    @classmethod
    def from_str(cls, string: str):
        return cls(string.split(","))

    def as_str(self):
        return ",".join(self)

    def subset_if_in_other_group_order(self, other_group_order: "GroupOrder"):
        return GroupOrder([item for item in self if item in other_group_order])

    def missing_but_in_other_group_order(self, other_group_order: "GroupOrder"):
        return GroupOrder(in_x_not_in_y(list(other_group_order), list(self)))

    def in_my_group_order_but_missing_from_other_group_order(
        self, other_group_order: "GroupOrder"
    ):
        return GroupOrder(in_x_not_in_y(list(self), list(other_group_order)))

    def me_but_with_other_groups_removed(self, other_group_order: "GroupOrder"):
        return GroupOrder([item for item in self if item not in other_group_order])


def get_group_order_from_dict_of_df_given_report_parameters(
    dict_of_df: Dict[str, pd.DataFrame],
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
) -> GroupOrder:
    list_of_groups = []
    for df in dict_of_df.values():
        groups_this_df = get_group_order_from_df_given_report_parameters(
            df=df,
            specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
        )
        list_of_groups += groups_this_df

    unique_list_of_groups = list(set(list_of_groups))

    all_groups_in_order = specific_parameters_for_type_of_report.group_order
    list_of_groups_order_preserved = [group for group in all_groups_in_order if group in unique_list_of_groups]

    return GroupOrder(list_of_groups_order_preserved)


def get_group_order_from_df_given_report_parameters(
    df: pd.DataFrame,
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
) -> List[str]:
    if len(df) == 0:
        return []
    copy_df = copy(df)
    column_name_to_group_by = specific_parameters_for_type_of_report.group_by_column
    column_to_group_by = list(copy_df[column_name_to_group_by])
    all_groups_in_order = specific_parameters_for_type_of_report.group_order
    list_of_groups = [group for group in all_groups_in_order if group in column_to_group_by]

    return list_of_groups


def get_group_order_excluding_missing_groups(
    dict_of_df,
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
) -> GroupOrder:
    group_order_from_df = get_group_order_from_dict_of_df_given_report_parameters(
        dict_of_df=dict_of_df,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
    )

    return group_order_from_df


def get_groups_in_dict_missing_from_group_order(
    dict_of_df: Dict[str, pd.DataFrame],
    group_order: GroupOrder,
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
) -> GroupOrder:
    group_order_from_df = get_group_order_from_dict_of_df_given_report_parameters(
        dict_of_df=dict_of_df,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
    )

    return group_order.missing_but_in_other_group_order(group_order_from_df)



def get_groups_in_group_order_missing_from_dict(
    dict_of_df,
    group_order: GroupOrder,
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
) -> GroupOrder:
    group_order_from_df = get_group_order_from_dict_of_df_given_report_parameters(
        dict_of_df=dict_of_df,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
    )

    return group_order.in_my_group_order_but_missing_from_other_group_order(
        group_order_from_df
    )

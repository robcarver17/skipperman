from typing import List, Dict
import pandas as pd

from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)

class GroupOrder(List[str]):
    pass

def get_group_order_from_dict_of_df_given_report_parameters(
    dict_of_df: Dict[str, pd.DataFrame],
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
) -> GroupOrder:

    list_of_groups = []
    for df in dict_of_df.values():
        groups_this_df = get_group_order_from_df_given_report_parameters(df=df, specific_parameters_for_type_of_report=specific_parameters_for_type_of_report)
        list_of_groups+= groups_this_df

    list_of_groups = list(set(list_of_groups))

    return GroupOrder(list_of_groups)

def get_group_order_from_df_given_report_parameters(
    df: pd.DataFrame,
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
)-> List[str]:
    if len(df)==0:
        return []
    grouped_df = df.groupby(specific_parameters_for_type_of_report.group_by_column)
    list_of_groups = list(grouped_df.groups.keys())

    return list_of_groups

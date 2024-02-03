from typing import List
import pandas as pd

from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)

class GroupOrder(List[str]):
    pass

def get_group_order_from_df_given_report_parameters(
    df: pd.DataFrame,
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
) -> GroupOrder:
    grouped_df = df.groupby(specific_parameters_for_type_of_report.group_by_column)
    list_of_groups = list(grouped_df.groups.keys())

    return GroupOrder(list_of_groups)

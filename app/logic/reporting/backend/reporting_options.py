import pandas as pd
from dataclasses import dataclass
from typing import List

from app.objects.reporting_options import PrintOptions, MarkedUpListFromDfParameters, ArrangeGroupsOptions


@dataclass
class MarkedUpListFromDfParametersWithActualGroupOrder:
    entry_columns: List[str]
    group_by_column: str
    actual_group_order: list
    include_group_as_header: bool = True
    first_value_in_group_is_key: bool = False
    prepend_group_name: bool = False

    @classmethod
    def from_marked_up_list_and_print_options_with_suggested_group_order(
        cls,
            print_options: PrintOptions,
        marked_up_list_from_df_parameters: MarkedUpListFromDfParameters,
        actual_group_order,
    ):

        return cls(
            entry_columns=marked_up_list_from_df_parameters.entry_columns,
            group_by_column=marked_up_list_from_df_parameters.group_by_column,
            actual_group_order=actual_group_order,
            include_group_as_header=print_options.include_group_as_header,
            first_value_in_group_is_key=print_options.first_value_in_group_is_key,
            prepend_group_name=print_options.prepend_group_name,
        )


### Bring everything together
@dataclass
class ReportingOptions:
    arrange_groups: ArrangeGroupsOptions
    marked_up_list_from_df: MarkedUpListFromDfParameters
    print_options: PrintOptions


@dataclass
class ReportingOptionsForSpecificGroupsInReport(ReportingOptions):
    arrange_groups: ArrangeGroupsOptions
    marked_up_list_from_df: MarkedUpListFromDfParametersWithActualGroupOrder
    print_options: PrintOptions
    list_of_groups: list

    ## only need to include things that will be accessed from 'wrong' place
    @property
    def landscape(self):
        return self.print_options.landscape

    @property
    def equalise_columns(self) -> bool:
        return self.print_options.equalise_column_width

    @property
    def height_of_title_in_characters(self) -> int:
        return self.print_options.height_of_title_in_characters

    @property
    def actual_group_order(self) -> List[str]:
        return self.marked_up_list_from_df.actual_group_order



def adjust_reporting_options_to_reflect_passed_dataframe(
    df: pd.DataFrame, reporting_options_before_adjustment: ReportingOptions
) -> ReportingOptionsForSpecificGroupsInReport:

    list_of_groups_in_df = get_list_of_natural_groups_from_df(
        df=df,
        marked_up_list_from_df_parameters=reporting_options_before_adjustment.marked_up_list_from_df,
    )

    marked_up_list_from_df_with_adjusted_groups = adjust_df_parameters_to_reflect_actual_groups_and_add_print_options(
        marked_up_list_from_df_parameters=reporting_options_before_adjustment.marked_up_list_from_df,
        list_of_groups_in_df=list_of_groups_in_df,
        print_options=reporting_options_before_adjustment.print_options
    )

    return ReportingOptionsForSpecificGroupsInReport(
        marked_up_list_from_df=marked_up_list_from_df_with_adjusted_groups,
        list_of_groups=list_of_groups_in_df,
        print_options=reporting_options_before_adjustment.print_options,
        arrange_groups=reporting_options_before_adjustment.arrange_groups,
    )


def get_list_of_natural_groups_from_df(
    df: pd.DataFrame,
    marked_up_list_from_df_parameters: MarkedUpListFromDfParameters,
) -> list:
    grouped_df = df.groupby(marked_up_list_from_df_parameters.group_by_column)
    list_of_groups = list(grouped_df.groups.keys())

    return list_of_groups


def adjust_df_parameters_to_reflect_actual_groups_and_add_print_options(
    marked_up_list_from_df_parameters: MarkedUpListFromDfParameters,
        print_options: PrintOptions,
    list_of_groups_in_df: list,
) -> MarkedUpListFromDfParametersWithActualGroupOrder:

    ## retains order but only for elements present
    passed_order_of_groups_in_marked_up_list = (
        marked_up_list_from_df_parameters.passed_group_order
    )
    actual_group_order = [
        group
        for group in passed_order_of_groups_in_marked_up_list
        if group in list_of_groups_in_df
    ]

    marked_up_list_from_df_parameters_with_actual_group_order = MarkedUpListFromDfParametersWithActualGroupOrder.from_marked_up_list_and_print_options_with_suggested_group_order(
        actual_group_order=actual_group_order,
        marked_up_list_from_df_parameters=marked_up_list_from_df_parameters,
        print_options=print_options
    )

    return marked_up_list_from_df_parameters_with_actual_group_order

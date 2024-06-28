from typing import Dict

import pandas as pd

from app.backend.reporting.options_and_parameters.report_options import ReportingOptions
from app.backend.reporting.process_stages.create_list_of_columns_from_groups import (
    get_order_of_indices_even_sizing_with_parameters,
)

from app.backend.reporting.arrangement.arrange_options import (
    ArrangementOptionsAndGroupOrder,
)

from app.logic.reporting.shared.arrangement_state import (
    get_stored_arrangement_and_group_order,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.reporting.constants import GROUP_ORDER
from app.backend.reporting.arrangement.group_order import (
    GroupOrder,
    get_group_order_excluding_missing_groups,
    get_groups_in_dict_missing_from_group_order,
    get_groups_in_group_order_missing_from_dict,
)
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)


def get_arrangement_options_and_group_order_from_stored_or_defaults(
    interface: abstractInterface,
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
    dict_of_df: Dict[str, pd.DataFrame],
) -> ArrangementOptionsAndGroupOrder:
    arrangement_options_and_group_order = get_stored_arrangement_and_group_order(
        interface=interface,
        report_type=specific_parameters_for_type_of_report.report_type,
    )
    if arrangement_options_and_group_order.is_empty():
        print("Empty arrangement, creating new one")
        arrangement_options_and_group_order = get_arrangement_options_from_df_and_specific_parameters(
            specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
            dict_of_df=dict_of_df,
        )

    return arrangement_options_and_group_order


def get_arrangement_options_from_df_and_specific_parameters(
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
    dict_of_df: Dict[str, pd.DataFrame],
) -> ArrangementOptionsAndGroupOrder:
    default_group_order = GroupOrder(
        specific_parameters_for_type_of_report.passed_group_order
    )
    filtered_group_order = get_group_order_excluding_missing_groups(
        dict_of_df=dict_of_df,
        group_order=default_group_order,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
    )

    arrangement_of_columns = get_order_of_indices_even_sizing_with_parameters(
        len(filtered_group_order), landscape=True
    )  ## only approximate

    return ArrangementOptionsAndGroupOrder.from_group_order_and_column_arrangements(
        group_order=filtered_group_order, arrangement_of_columns=arrangement_of_columns
    )


def get_missing_groups(reporting_options: ReportingOptions) -> GroupOrder:
    group_order = reporting_options.arrange_options_and_group_order.group_order
    dict_of_df = reporting_options.dict_of_df
    specific_parameters = reporting_options.specific_parameters

    missing_groups = get_groups_in_dict_missing_from_group_order(
        dict_of_df=dict_of_df,
        group_order=group_order,
        specific_parameters_for_type_of_report=specific_parameters,
    )
    return GroupOrder(missing_groups)


def get_empty_groups(reporting_options: ReportingOptions) -> GroupOrder:
    group_order = reporting_options.arrange_options_and_group_order.group_order
    dict_of_df = reporting_options.dict_of_df
    specific_parameters = reporting_options.specific_parameters

    empty_groups = get_groups_in_group_order_missing_from_dict(
        dict_of_df=dict_of_df,
        group_order=group_order,
        specific_parameters_for_type_of_report=specific_parameters,
    )
    return GroupOrder(empty_groups)

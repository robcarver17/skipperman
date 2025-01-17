from typing import Dict

import pandas as pd

from app.backend.reporting.arrangement.arrange_options import ArrangementOptionsAndGroupOrder

from app.backend.reporting.arrangement.get_and_update_arrangement_options import (
    get_stored_arrangement_and_group_order,
)
from app.backend.reporting.options_and_parameters.report_options import ReportingOptions
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import \
    SpecificParametersForTypeOfReport
from app.backend.reporting.process_stages.create_list_of_columns_from_groups import \
    get_order_of_indices_even_sizing_with_parameters
from app.data_access.store.object_store import ObjectStore

from app.backend.reporting.arrangement.group_order import (
    GroupOrder,
    get_group_order_excluding_missing_groups,
    get_groups_in_dict_missing_from_group_order,
    get_groups_in_group_order_missing_from_dict,
)


def get_arrangement_options_and_group_order_from_stored_or_defaults(
    object_store: ObjectStore,
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
    dict_of_df: Dict[str, pd.DataFrame],
) -> ArrangementOptionsAndGroupOrder:
    arrangement_options_and_group_order = get_stored_arrangement_and_group_order(
        object_store=object_store,
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

    filtered_group_order = get_group_order_excluding_missing_groups(
        dict_of_df=dict_of_df,
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

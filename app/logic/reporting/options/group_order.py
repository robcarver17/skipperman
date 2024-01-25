import pandas as pd

from app.logic.abstract_interface import abstractInterface
from app.logic.reporting.constants import GROUP_ORDER
from app.objects.constants import missing_data
from app.reporting.arrangement.group_order import get_group_order_from_df_given_report_parameters, GroupOrder
from app.reporting.options_and_parameters.report_type_specific_parameters import SpecificParametersForTypeOfReport


def get_group_order_from_stored_or_df(
    interface: abstractInterface,
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
    df: pd.DataFrame,
) -> GroupOrder:
    groups = get_stored_group_order(interface)
    if groups is missing_data:
        groups_if_not_stored = get_group_order_from_df_given_report_parameters(
            df=df,
            specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
        )
        save_group_order_to_storage(
            interface=interface, groups_in_order=groups_if_not_stored
        )
        return groups_if_not_stored
    else:
        return GroupOrder(groups)


def get_stored_group_order(interface: abstractInterface) -> list:
    groups = interface.get_persistent_value(GROUP_ORDER)
    return groups


def save_group_order_to_storage(interface: abstractInterface, groups_in_order: list):
    interface.set_persistent_value(GROUP_ORDER, groups_in_order)

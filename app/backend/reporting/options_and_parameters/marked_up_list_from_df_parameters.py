from dataclasses import dataclass
from typing import Dict

from app.backend.reporting.arrangement.group_order import GroupOrder
from app.backend.reporting.options_and_parameters.print_options import PrintOptions
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport, GroupAnnotations,
)
from app.objects.utilities.exceptions import arg_not_passed


@dataclass
class MarkedUpListFromDfParametersWithActualGroupOrder:
    actual_group_order: GroupOrder
    include_group_as_header: bool = True
    first_value_in_group_is_key: bool = False
    prepend_group_name: bool = False
    group_by_column: str = arg_not_passed
    include_size_of_group_if_header: bool = False
    include_row_count: bool = False
    drop_group_name_from_columns: bool = False
    group_annotations: GroupAnnotations = arg_not_passed

def create_parameters_to_create_marked_up_list_from_df(
    print_options: PrintOptions,
    specific_parameters: SpecificParametersForTypeOfReport,
    group_order: GroupOrder,
) -> MarkedUpListFromDfParametersWithActualGroupOrder:
    return MarkedUpListFromDfParametersWithActualGroupOrder(
        #            entry_columns=specific_parameters.entry_columns,
        group_by_column=specific_parameters.group_by_column,
        actual_group_order=group_order,
        include_group_as_header=print_options.include_group_as_header,
        first_value_in_group_is_key=print_options.first_value_in_group_is_key,
        prepend_group_name=print_options.prepend_group_name,
        include_size_of_group_if_header=print_options.include_size_of_group_if_header,
        group_annotations = specific_parameters.group_annotations,
        include_row_count = print_options.include_row_count,
        drop_group_name_from_columns=print_options.drop_group_from_columns
    )

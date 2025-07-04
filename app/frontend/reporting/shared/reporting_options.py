from typing import List, Dict

import numpy as np
import pandas as pd

from app.backend.reporting.options_and_parameters.marked_up_list_from_df_parameters import (
    create_parameters_to_create_marked_up_list_from_df,
)
from app.backend.reporting.arrangement.get_and_update_arrangement_options import (
    reset_arrangement_report_options,
)
from app.backend.reporting.options_and_parameters.print_options import PrintOptions
from app.backend.reporting.options_and_parameters.report_options import ReportingOptions
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)
from app.backend.reporting.process_stages.create_list_of_groups_from_df import (
    get_dict_of_grouped_df,
)
from app.backend.reporting.report_generator import ReportGenerator
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.reporting.shared.group_order import (
    get_arrangement_options_and_group_order_from_stored_or_defaults,
)
from app.frontend.reporting.shared.print_options import (
    get_saved_print_options,
    reset_print_report_options,
    override_print_options_with_new_values,
)
from app.objects.utilities.exceptions import arg_not_passed


def augment_order_of_groups_with_sizes(reporting_options: ReportingOptions) -> list:
    dict_of_grouped_df = get_dict_of_grouped_df(
        dict_of_df=reporting_options.dict_of_df,
        marked_up_list_from_df_parameters=reporting_options.marked_up_list_from_df_parameters,
    )

    list_of_sizes = [grouped_df.size() for grouped_df in dict_of_grouped_df.values()]
    sizes = from_list_of_sizes_to_single_list(list_of_sizes)

    return [
        "%s (%d)" % (group, get_group_size(group, sizes))
        for group in reporting_options.group_order
    ]


def get_group_size(group: str, sizes: Dict[str, int]):
    if group not in sizes.keys():
        return 0
    else:
        return sizes[group]


def from_list_of_sizes_to_single_list(
    list_of_sizes: List[Dict[str, int]]
) -> Dict[str, int]:
    all_groups = []
    for size_dict in list_of_sizes:
        all_groups += list(size_dict.keys())
    all_groups = list(set(all_groups))

    sizes = {}
    for group in all_groups:
        list_of_total_size = [
            size_dict.get(group, np.nan) for size_dict in list_of_sizes
        ]
        avg_size = int(np.ceil(np.nanmean(list_of_total_size)))
        sizes[group] = avg_size

    return sizes


def get_reporting_options(
    interface: abstractInterface,
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
    dict_of_df: Dict[str, pd.DataFrame],
    ignore_stored_print_option_values_and_use_default: bool = False,
    override_print_options: dict = arg_not_passed,
) -> ReportingOptions:
    arrangement_options_and_group_order = get_arrangement_options_and_group_order_from_stored_or_defaults(
        object_store=interface.object_store,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
        dict_of_df=dict_of_df,
    )

    print_options = get_saved_print_options(
        interface=interface,
        report_type=specific_parameters_for_type_of_report.report_type,
        ignore_stored_values_and_use_default=ignore_stored_print_option_values_and_use_default,
    )

    if not override_print_options is arg_not_passed:
        print_options = override_print_options_with_new_values(
            print_options, **override_print_options
        )

    marked_up_list_from_df_parameters_with_actual_group_order = (
        create_parameters_to_create_marked_up_list_from_df(
            print_options=print_options,
            specific_parameters=specific_parameters_for_type_of_report,
            group_order=arrangement_options_and_group_order.group_order,
        )
    )

    return ReportingOptions(
        arrange_options_and_group_order=arrangement_options_and_group_order,
        specific_parameters=specific_parameters_for_type_of_report,
        dict_of_df=dict_of_df,
        print_options=print_options,
        marked_up_list_from_df_parameters=marked_up_list_from_df_parameters_with_actual_group_order,
    )


def reset_all_report_options(
    interface: abstractInterface, report_generator: ReportGenerator
):
    reset_print_report_options(interface=interface, report_generator=report_generator)
    reset_specific_report_options(
        interface=interface, report_generator=report_generator
    )
    reset_arrangement_report_options(
        object_store=interface.object_store, report_generator=report_generator
    )


def reset_specific_report_options(
    interface: abstractInterface, report_generator: ReportGenerator
):
    report_generator.clear_additional_parameters(interface)

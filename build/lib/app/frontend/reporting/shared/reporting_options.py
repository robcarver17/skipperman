from typing import List, Dict

import numpy as np
import pandas as pd

from app.backend.reporting.options_and_parameters.marked_up_list_from_df_parameters import (
    create_parameters_to_create_marked_up_list_from_df,
)
from app.backend.reporting import (
    ReportingOptions,
)
from app.backend.reporting import (
    SpecificParametersForTypeOfReport,
)
from app.backend.reporting import (
    get_dict_of_grouped_df,
)
from app.backend.reporting.arrangement.arrange_options import reset_arrangement_report_options
from app.frontend.reporting.shared.report_generator import ReportGenerator
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.reporting.shared.group_order import (
    get_arrangement_options_and_group_order_from_stored_or_defaults,
)
from app.frontend.reporting.shared.print_options import (
    get_saved_print_options,
    reset_print_report_options,
)


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
) -> ReportingOptions:
    arrangement_options_and_group_order = get_arrangement_options_and_group_order_from_stored_or_defaults(
        interface=interface,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
        dict_of_df=dict_of_df,
    )

    print_options = get_saved_print_options(
        interface=interface,
        report_type=specific_parameters_for_type_of_report.report_type,
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
    reset_print_report_options(interface, report_generator)
    reset_specific_report_options(interface, report_generator)
    reset_arrangement_report_options(interface, report_generator)


def reset_specific_report_options(
    interface: abstractInterface, report_generator: ReportGenerator
):
    report_generator.clear_additional_parameters(interface)

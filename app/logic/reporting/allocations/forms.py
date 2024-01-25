from typing import Tuple

from app.objects.abstract_objects.abstract_form import (
    yes_no_radio,
)
from app.objects.abstract_objects.abstract_text import bold
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.logic.abstract_interface import abstractInterface
from app.logic.reporting.allocations.processes import (
    get_group_order_for_allocation_report,
    load_additional_parameters_for_allocation_report
)
from app.logic.reporting.constants import SHOW_FULL_NAMES, INCLUDE_UNALLOCATED_CADETS
from app.logic.reporting.options.arrangements import get_stored_arrangement
from app.logic.reporting.options.print_options import (
    get_saved_print_options,
    report_print_options_as_list_of_lines,
)
from app.reporting.arrangement.arrange_options import describe_arrangement
from app.reporting.allocation_report import AdditionalParametersForAllocationReport, specific_parameters_for_allocation_report


def reporting_options_form_for_group_additional_parameters(
    interface: abstractInterface,
) -> ListOfLines:
    additional_parameters = load_additional_parameters_for_allocation_report(interface)
    my_options = ListOfLines(
        [
            yes_no_radio(
                input_label="Show full names? (no to include first initial and surname only)",
                input_name=SHOW_FULL_NAMES,
                default_is_yes=additional_parameters.display_full_names,
            ),
            yes_no_radio(
                input_label="Include unallocated cadets?",
                input_name=INCLUDE_UNALLOCATED_CADETS,
                default_is_yes=additional_parameters.include_unallocated_cadets,
            ),
            _______________,
        ]
    )
    return my_options


def get_text_explaining_various_options_for_allocations_report(
    interface: abstractInterface,
) -> Tuple[ListOfLines, ListOfLines, ListOfLines]:
    additional_parameters = load_additional_parameters_for_allocation_report(interface)
    additional_options_as_text = explain_additional_parameters(additional_parameters)

    print_options = get_saved_print_options(report_type=specific_parameters_for_allocation_report.report_type, interface=interface)
    print_options_as_text = report_print_options_as_list_of_lines(print_options)
    print_options_as_text = ListOfLines([bold("Print Options:"), print_options_as_text])

    order_of_groups = get_group_order_for_allocation_report(interface)
    order_of_groups_as_text = ", ".join(order_of_groups)

    arrangement = get_stored_arrangement(interface)
    arrangement_text = describe_arrangement(arrangement)

    arrangement_and_order_text = ListOfLines(
        [
            bold("Order and arrangement of groups:"),
            "Order: %s" % order_of_groups_as_text,
            "Arrangement: %s" % arrangement_text,
        ]
    )

    return additional_options_as_text, print_options_as_text, arrangement_and_order_text


def explain_additional_parameters(
    additional_parameters: AdditionalParametersForAllocationReport,
) -> ListOfLines:
    if additional_parameters.display_full_names:
        name_str = "Display cadet full names"
    else:
        name_str = "Display initial and surname only"
    if additional_parameters.include_unallocated_cadets:
        alloc_str = "Include all cadets, even those not allocated to groups"
    else:
        alloc_str = "Exclude unallocated cadets"

    return ListOfLines([name_str, alloc_str])

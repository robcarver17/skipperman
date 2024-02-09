from typing import Tuple

from app.backend.reporting.allocation_report import specific_parameters_for_allocation_report
from app.backend.reporting.arrangement.arrange_options import describe_arrangement
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.reporting.allocations.forms import explain_additional_parameters_for_allocation_report
from app.logic.reporting.allocations.processes import load_additional_parameters_for_allocation_report, \
    get_group_order_for_allocation_report
from app.logic.reporting.options.arrangement_state import get_stored_arrangement
from app.logic.reporting.options.print_options import get_saved_print_options, report_print_options_as_list_of_lines
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.abstract_objects.abstract_text import bold


def get_text_explaining_various_options_for_rota_report(
    interface: abstractInterface,
) -> Tuple[ListOfLines, ListOfLines, ListOfLines]:
    additional_parameters = load_additional_parameters_for_allocation_report(interface)
    additional_options_as_text = explain_additional_parameters_for_allocation_report(additional_parameters)

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

def explain_additional_parameters_for_rota_report(
    additional_parameters: AdditionalParametersForAllocationReport,
) -> ListOfLines:
    if additional_parameters.display_full_names:
        name_str = "Display cadet full names"
    else:
        name_str = "Display initial and surname only"
    if additional_parameters.include_unallocated_cadets:
        alloc_str = "Include all group_allocations, even those not allocated to groups"
    else:
        alloc_str = "Exclude unallocated group_allocations"

    return ListOfLines([name_str, alloc_str])

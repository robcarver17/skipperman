from typing import Tuple

from app.objects.abstract_objects.abstract_form import (
    yes_no_radio,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________, Line
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.reporting.allocations.processes import (
    load_additional_parameters_for_allocation_report, SHOW_FULL_NAMES, INCLUDE_UNALLOCATED_CADETS
)
from app.backend.reporting.allocation_report.allocation_report import AdditionalParametersForAllocationReport


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
                input_label="Include unallocated group_allocations? (Changing will reset group order and arrangement)",
                input_name=INCLUDE_UNALLOCATED_CADETS,
                default_is_yes=additional_parameters.include_unallocated_cadets,
            ),
            _______________,
        ]
    )
    return my_options.add_Lines()


def explain_additional_parameters_for_allocation_report(interface: abstractInterface,
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

    return ListOfLines([Line(name_str), Line(alloc_str)])

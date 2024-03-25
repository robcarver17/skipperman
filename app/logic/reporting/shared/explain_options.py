from typing import Tuple

from app.backend.reporting.arrangement.arrange_options import describe_arrangement
from app.logic.reporting.shared.arrangement_state import get_stored_arrangement
from app.logic.reporting.shared.group_order import get_group_order_for_generic_report
from app.logic.reporting.shared.print_options import get_saved_print_options, report_print_options_as_list_of_lines
from app.logic.reporting.shared.report_generator import ReportGenerator
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.abstract_objects.abstract_text import bold


def get_text_explaining_various_options_for_generic_report(
    interface: abstractInterface,
    report_generator: ReportGenerator
) -> Tuple[
    ListOfLines, ListOfLines, ListOfLines]:
    additional_parameters = report_generator.load_additional_parameters(interface)
    additional_options_as_text =report_generator.explain_additional_parameters(interface=interface, additional_parameters=additional_parameters)

    print_options = get_saved_print_options(report_type=report_generator.specific_parameters_for_type_of_report.report_type, interface=interface)
    print_options_as_text = report_print_options_as_list_of_lines(print_options)
    print_options_as_text = ListOfLines([bold("Print Options:"), print_options_as_text])

    order_of_groups = get_group_order_for_generic_report(interface=interface, report_generator=report_generator)
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

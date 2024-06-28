from typing import Tuple

from app.backend.reporting.options_and_parameters.report_options import ReportingOptions

from app.backend.reporting.arrangement.arrange_options import describe_arrangement
from app.backend.reporting.arrangement.group_order import (
    GroupOrder,
    get_group_order_excluding_missing_groups,
    get_groups_in_dict_missing_from_group_order,
)
from app.logic.reporting.shared.arrangement_state import (
    get_stored_arrangement_and_group_order,
)
from app.logic.reporting.shared.group_order import (
    get_arrangement_options_and_group_order_from_stored_or_defaults,
)
from app.logic.reporting.shared.print_options import (
    get_saved_print_options,
    report_print_options_as_list_of_lines,
)
from app.logic.reporting.shared.report_generator import ReportGenerator
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.abstract_objects.abstract_text import bold


def get_text_explaining_various_options_for_generic_report(
    interface: abstractInterface, report_generator: ReportGenerator
) -> Tuple[ListOfLines, ListOfLines, ListOfLines]:
    additional_parameters = report_generator.load_additional_parameters(interface)
    additional_options_as_text = report_generator.explain_additional_parameters(
        interface=interface, additional_parameters=additional_parameters
    )

    print_options = get_saved_print_options(
        report_type=report_generator.specific_parameters_for_type_of_report.report_type,
        interface=interface,
    )
    print_options_as_text = report_print_options_as_list_of_lines(print_options)
    print_options_as_text = ListOfLines(
        [Line(bold("Print Options:")), print_options_as_text]
    )

    arrangement_and_order_text = get_arrangement_options_and_group_order_text(
        interface=interface, report_generator=report_generator
    )

    return additional_options_as_text, print_options_as_text, arrangement_and_order_text


def get_arrangement_options_and_group_order_text(
    interface: abstractInterface, report_generator: ReportGenerator
) -> ListOfLines:
    dict_of_df = report_generator.get_dict_of_df(interface)

    if len(dict_of_df) == 0:
        return ListOfLines(
            [
                "Report has no content - change filter or you might need to allocate groups or volunteers first to get results"
            ]
        )

    arrangement_options_and_group_order = get_arrangement_options_and_group_order_from_stored_or_defaults(
        interface=interface,
        specific_parameters_for_type_of_report=report_generator.specific_parameters_for_type_of_report,
        dict_of_df=dict_of_df,
    )
    group_order = arrangement_options_and_group_order.group_order
    filtered_group_order = get_group_order_excluding_missing_groups(
        dict_of_df=dict_of_df,
        group_order=group_order,
        specific_parameters_for_type_of_report=report_generator.specific_parameters_for_type_of_report,
    )

    missing_groups = get_groups_in_dict_missing_from_group_order(
        dict_of_df=dict_of_df,
        group_order=group_order,
        specific_parameters_for_type_of_report=report_generator.specific_parameters_for_type_of_report,
    )

    order_of_groups_as_text = ", ".join(filtered_group_order)

    if len(missing_groups) == 0:
        missing_line = ""
    else:
        order_of_missing_groups_as_text = ", ".join(missing_groups)
        warning = (
            "FOLLOWING GROUPS ARE IN DATA, BUT NOT INCLUDED IN REPORT: %s (CHANGE ARRANGEMENT TO INCLUDE)"
            % order_of_missing_groups_as_text
        )
        missing_line = Line(bold(warning))
        interface.log_error(warning)

    arrangement = get_stored_arrangement_and_group_order(
        interface=interface,
        report_type=report_generator.specific_parameters_for_type_of_report.report_type,
    ).arrangement_options
    arrangement_text = describe_arrangement(arrangement)

    return ListOfLines(
        [
            Line(bold("Order and arrangement of groups:")),
            Line("Order: %s" % order_of_groups_as_text),
            missing_line,
            Line("Arrangement: %s" % arrangement_text),
        ]
    )

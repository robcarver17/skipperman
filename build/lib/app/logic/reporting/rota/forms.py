from typing import Tuple

from app.backend.reporting.rota_report.configuration import specific_parameters_for_volunteer_report, AdditionalParametersForVolunteerReport
from app.logic.events.events_in_state import get_event_from_state
from app.logic.reporting.rota.processes import DAYS_TO_SHOW
from app.backend.reporting.arrangement.arrange_options import describe_arrangement
from app.backend.forms.form_utils import get_availability_checkbox
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.logic.reporting.rota.processes import get_group_order_for_volunteer_report
from app.logic.reporting.rota.processes import load_additional_parameters_for_rota_report
from app.logic.reporting.shared.arrangement_state import get_stored_arrangement
from app.logic.reporting.shared.print_options import get_saved_print_options, report_print_options_as_list_of_lines
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_text import bold


def get_text_explaining_various_options_for_rota_report(
    interface: abstractInterface,
) -> Tuple[ListOfLines, ListOfLines, ListOfLines]:
    additional_parameters = load_additional_parameters_for_rota_report(interface)
    additional_options_as_text = explain_additional_parameters_for_rota_report(additional_parameters)

    print_options = get_saved_print_options(report_type=specific_parameters_for_volunteer_report.report_type, interface=interface)
    print_options_as_text = report_print_options_as_list_of_lines(print_options)
    print_options_as_text = ListOfLines([bold("Print Options:"), print_options_as_text])

    order_of_groups = get_group_order_for_volunteer_report(interface)
    order_of_groups_as_text = ", ".join(order_of_groups)

    arrangement = get_stored_arrangement(interface)
    arrangement_text = describe_arrangement(arrangement)

    arrangement_and_order_text = ListOfLines(
        [
            bold("Order and arrangement of volunteer teams:"),
            "Order: %s" % order_of_groups_as_text,
            "Arrangement: %s" % arrangement_text,
        ]
    )

    return additional_options_as_text, print_options_as_text, arrangement_and_order_text

def explain_additional_parameters_for_rota_report(
    additional_parameters: AdditionalParametersForVolunteerReport, ## should be rota
) -> ListOfLines:

    return ListOfLines(["Report covers the following days: %s" % str(additional_parameters.days_to_show)])

def reporting_options_form_for_rota_additional_parameters(
    interface: abstractInterface,
) -> ListOfLines:
    additional_parameters = load_additional_parameters_for_rota_report(interface)
    event = get_event_from_state(interface)
    choose_days = get_availability_checkbox(input_name=DAYS_TO_SHOW,
                                            availability=additional_parameters.days_to_show,
                                            line_break=True,
                                            include_all=True,
                                            event=event)

    my_options = ListOfLines(
        [
            "Select days in the event you wish to include in the report rota:",
            choose_days,
            _______________,
        ]
    )
    return my_options


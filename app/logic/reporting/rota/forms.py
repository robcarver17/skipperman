from app.backend.reporting.rota_report.configuration import AdditionalParametersForVolunteerReport
from app.logic.events.events_in_state import get_event_from_state
from app.logic.reporting.rota.processes import DAYS_TO_SHOW
from app.backend.forms.form_utils import get_availability_checkbox
from app.objects.abstract_objects.abstract_interface import abstractInterface


from app.logic.reporting.rota.processes import load_additional_parameters_for_rota_report
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________


def explain_additional_parameters_for_rota_report(interface: abstractInterface,
    additional_parameters: AdditionalParametersForVolunteerReport, ## should be rota
) -> ListOfLines:

    return ListOfLines(["Report covers the following days: %s" % str(additional_parameters.days_to_show)]).add_Lines()

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

    return my_options.add_Lines()


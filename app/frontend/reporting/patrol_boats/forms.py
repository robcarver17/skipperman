from app.backend.reporting.patrol_boat_report.configuration import (
    AdditionalParametersForPatrolBoatReport,
)
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.reporting.patrol_boats.processes import (
    DAYS_TO_SHOW,
)
from app.frontend.forms.form_utils import get_availability_checkbox
from app.objects.abstract_objects.abstract_interface import abstractInterface


from app.frontend.reporting.patrol_boats.processes import (
    load_additional_parameters_for_patrol_boats_report,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________


def explain_additional_parameters_for_patrol_boats_report(
    interface: abstractInterface,  ## required by default but not used
    additional_parameters: AdditionalParametersForPatrolBoatReport,
) -> ListOfLines:
    days = "Report covers the following days: %s" % str(
        additional_parameters.days_to_show.days_available_as_str()
    )

    return ListOfLines([days]).add_Lines()


def reporting_options_form_for_patrol_boats_additional_parameters(
    interface: abstractInterface,
) -> ListOfLines:
    additional_parameters = load_additional_parameters_for_patrol_boats_report(
        interface
    )
    event = get_event_from_state(interface)
    choose_days = get_availability_checkbox(
        input_name=DAYS_TO_SHOW,
        availability=additional_parameters.days_to_show,
        line_break=True,
        include_all=True,
        event=event,
    )

    my_options = ListOfLines(
        [
            "Select days in the event you wish to include in the report:",
            choose_days,
            _______________,
        ]
    )

    return my_options.add_Lines()

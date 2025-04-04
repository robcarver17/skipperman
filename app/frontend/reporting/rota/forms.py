from app.backend.patrol_boats.volunteers_at_event_on_patrol_boats import (
    no_volunteers_on_patrol_boats_at_event,
)
from app.objects.abstract_objects.abstract_form import yes_no_radio

from app.backend.reporting.rota_report.configuration import (
    AdditionalParametersForVolunteerReport,
)
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.reporting.rota.processes import (
    DAYS_TO_SHOW,
    BOATS,
    no_volunteers_on_power_boats_at_current_event,
)
from app.frontend.forms.form_utils import get_availability_checkbox
from app.objects.abstract_objects.abstract_interface import abstractInterface


from app.frontend.reporting.rota.processes import (
    load_additional_parameters_for_rota_report,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________


def explain_additional_parameters_for_rota_report(
    interface: abstractInterface,  ## required by default but not used
    additional_parameters: AdditionalParametersForVolunteerReport,  ## should be rota
) -> ListOfLines:
    days = "Report covers the following days: %s" % str(
        additional_parameters.days_to_show.days_available_as_str()
    )
    power_boats_only = additional_parameters.power_boats_only

    boats = (
        "Sort by power boats and exclude volunteers not on boats"
        if power_boats_only
        else ""
    )

    return ListOfLines([days, boats]).add_Lines()


def reporting_options_form_for_rota_additional_parameters(
    interface: abstractInterface,
) -> ListOfLines:
    additional_parameters = load_additional_parameters_for_rota_report(interface)
    event = get_event_from_state(interface)
    choose_days = get_availability_checkbox(
        input_name=DAYS_TO_SHOW,
        availability=additional_parameters.days_to_show,
        line_break=True,
        include_all=True,
        event=event,
    )
    if no_volunteers_on_power_boats_at_current_event(interface):
        boats = ""
    else:
        boats = yes_no_radio(
            input_label="Report for power boats only, sorted by power boat (will be ignored if sort by skills also set)",
            input_name=BOATS,
            default_is_yes=additional_parameters.power_boats_only,
        )

    my_options = ListOfLines(
        [
            "Select days in the event you wish to include in the report rota:",
            choose_days,
            _______________,
            boats,
            _______________,
        ]
    )

    return my_options.add_Lines()

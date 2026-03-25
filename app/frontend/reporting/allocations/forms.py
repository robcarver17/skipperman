from app.frontend.forms.form_utils import get_availability_checkbox
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_form import (
    yes_no_radio,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.reporting.allocations.processes import (
    load_additional_parameters_for_allocation_report,
    SHOW_FULL_NAMES,
    INCLUDE_UNALLOCATED_CADETS,
    CLUB_BOAT_ASTERIX,
    DAYS_TO_SHOW,
)
from app.backend.reporting.allocation_report.allocation_report import (
    AdditionalParametersForAllocationReport,
)


def reporting_options_form_for_group_additional_parameters(
    interface: abstractInterface,
) -> ListOfLines:
    additional_parameters = load_additional_parameters_for_allocation_report(interface)
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
            yes_no_radio(
                input_label="Show full names? (no to include first initial and surname only)",
                input_name=SHOW_FULL_NAMES,
                default_is_yes=additional_parameters.display_full_names,
            ),
            yes_no_radio(
                input_label="Include unallocated group allocations? (Changing will reset custom group arrangements)",
                input_name=INCLUDE_UNALLOCATED_CADETS,
                default_is_yes=additional_parameters.include_unallocated_cadets,
            ),
            yes_no_radio(
                input_label="Include asterix for club boat allocation?",
                input_name=CLUB_BOAT_ASTERIX,
                default_is_yes=additional_parameters.add_asterix_for_club_boats,
            ),
            _______________,
            "Select days in the event you wish to include in the report:",
            choose_days,
        ]
    )
    return my_options.add_Lines()


def explain_additional_parameters_for_allocation_report(
    interface: abstractInterface,  ## not used but always passed
    additional_parameters: AdditionalParametersForAllocationReport,
) -> ListOfLines:
    if additional_parameters.display_full_names:
        name_str = "Display cadet full names"
    else:
        name_str = "Display initial and surname only"
    if additional_parameters.include_unallocated_cadets:
        alloc_str = "Include all group allocations, even those not allocated to groups"
    else:
        alloc_str = "Exclude unallocated group allocations"
    if additional_parameters.add_asterix_for_club_boats:
        club_str = "Include * if club boat hired"
    else:
        club_str = "No * for club boats"
    days = "Report covers the following days: %s" % str(
        additional_parameters.days_to_show.days_available_as_str()
    )

    return ListOfLines([Line(name_str), Line(alloc_str), Line(club_str), Line(days)])

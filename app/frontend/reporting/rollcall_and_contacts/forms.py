from app.objects.abstract_objects.abstract_form import (
    yes_no_radio,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.reporting.rollcall_and_contacts.processes import (
    load_additional_parameters_for_rollcall_report,
    SHOW_FULL_NAMES,
    INCLUDE_UNALLOCATED_CADETS,
    CLUB_BOAT_ASTERIX,
    HEALTH_DATA,
    EMERGENCY_CONTACTS,
)
from app.backend.reporting.rollcall_report.configuration import (
    AdditionalParametersForRollcallReport,
)


def reporting_options_form_for_rollcall_additional_parameters(
    interface: abstractInterface,
) -> ListOfLines:
    additional_parameters = load_additional_parameters_for_rollcall_report(interface)
    my_options = ListOfLines(
        [
            yes_no_radio(
                input_label="Show full names? (no to include first initial and surname only)",
                input_name=SHOW_FULL_NAMES,
                default_is_yes=additional_parameters.display_full_names,
            ),
            yes_no_radio(
                input_label="Include unallocated group_rollcalls? (Changing will reset group order and arrangement)",
                input_name=INCLUDE_UNALLOCATED_CADETS,
                default_is_yes=additional_parameters.include_unallocated_cadets,
            ),
            yes_no_radio(
                input_label="Include asterix for club boat rollcall?",
                input_name=CLUB_BOAT_ASTERIX,
                default_is_yes=additional_parameters.add_asterix_for_club_boats,
            ),
            yes_no_radio(
                input_label="Include confidential health data?",
                input_name=HEALTH_DATA,
                default_is_yes=additional_parameters.include_health_data,
            ),
            yes_no_radio(
                input_label="Include private emergency contact details?",
                input_name=EMERGENCY_CONTACTS,
                default_is_yes=additional_parameters.incude_emergency_contacts,
            ),
            _______________,
        ]
    )
    return my_options.add_Lines()


def explain_additional_parameters_for_rollcall_report(
    interface: abstractInterface,
    additional_parameters: AdditionalParametersForRollcallReport,
) -> ListOfLines:
    if additional_parameters.display_full_names:
        name_str = "Display cadet full names"
    else:
        name_str = "Display initial and surname only"
    if additional_parameters.include_unallocated_cadets:
        alloc_str = "Include all cadets, even those not allocated to groups"
    else:
        alloc_str = "Exclude unallocated cadets"
    if additional_parameters.add_asterix_for_club_boats:
        club_str = "Include * if club boat hired"
    else:
        club_str = "No * for club boats"
    if additional_parameters.incude_emergency_contacts:
        contact_str = "Include *private* emergency contact data"
    else:
        contact_str = "Private contact data not included"
    if additional_parameters.include_health_data:
        health_str = "Include *confidential* health data"
    else:
        health_str = "Health data not included"

    return ListOfLines(
        [
            Line(name_str),
            Line(alloc_str),
            Line(health_str),
            Line(contact_str),
            Line(club_str),
        ]
    )

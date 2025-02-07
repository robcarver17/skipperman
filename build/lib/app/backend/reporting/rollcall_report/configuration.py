from dataclasses import dataclass
from app.objects.composed.cadets_at_event_with_groups import GROUP_STR_NAME
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)

all_groups_names = []
specific_parameters_for_rollcall_report = SpecificParametersForTypeOfReport(
    #    entry_columns=[CADET_NAME],
    group_by_column=GROUP_STR_NAME,
    report_type="Rollcall report",
)


@dataclass
class AdditionalParametersForRollcallReport:
    display_full_names: bool
    include_unallocated_cadets: bool
    add_asterix_for_club_boats: bool
    include_health_data: bool
    incude_emergency_contacts: bool

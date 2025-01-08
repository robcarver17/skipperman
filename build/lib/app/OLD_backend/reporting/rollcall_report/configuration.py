from dataclasses import dataclass
from app.objects.cadet_with_id_with_group_at_event import GROUP_STR_NAME
from app.backend.reporting import (
    SpecificParametersForTypeOfReport,
)

all_groups_names = []
specific_parameters_for_rollcall_report = SpecificParametersForTypeOfReport(
    #    entry_columns=[CADET_NAME],
    group_by_column=GROUP_STR_NAME,
    passed_group_order=all_groups_names,
    report_type="Rollcall report",
)


@dataclass
class AdditionalParametersForRollcallReport:
    display_full_names: bool
    include_unallocated_cadets: bool
    add_asterix_for_club_boats: bool
    include_health_data: bool
    incude_emergency_contacts: bool

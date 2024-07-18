from dataclasses import dataclass
from app.data_access.configuration.groups import all_groups_names
from app.objects.primtive_with_id.groups import CADET_NAME, GROUP_STR_NAME
from app.OLD_backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)

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

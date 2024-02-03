from dataclasses import dataclass
from app.data_access.configuration.configuration import ALL_GROUPS_NAMES
from app.objects.groups import CADET_NAME, GROUP_STR_NAME
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)

specific_parameters_for_allocation_report = SpecificParametersForTypeOfReport(
    entry_columns=[CADET_NAME],
    group_by_column=GROUP_STR_NAME,
    passed_group_order=ALL_GROUPS_NAMES,
    report_type="Allocation report"
)


@dataclass
class AdditionalParametersForAllocationReport:
    display_full_names: bool
    include_unallocated_cadets: bool

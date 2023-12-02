from dataclasses import dataclass
from app.data_access.configuration.configuration import ALL_GROUPS
from app.objects.field_list import CADET_NAME, GROUP_STR_NAME
from app.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)

specific_parameters_for_allocation_report = SpecificParametersForTypeOfReport(
    entry_columns=[CADET_NAME],
    group_by_column=GROUP_STR_NAME,
    passed_group_order=ALL_GROUPS,
    report_type="Allocation report"
)


@dataclass
class AdditionalParametersForAllocationReport:
    display_full_names: bool
    include_unallocated_cadets: bool

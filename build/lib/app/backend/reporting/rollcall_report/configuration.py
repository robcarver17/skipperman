from dataclasses import dataclass

from app.backend.groups.list_of_groups import get_list_of_groups
from app.data_access.store.object_store import ObjectStore
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)
from app.objects.groups import unallocated_group


GROUP_NAME_COLUMN_HEADING_FOR_SPOTTER_SHEET = "Group"
def get_specific_parameters_for_rollcall_report(object_store: ObjectStore) -> SpecificParametersForTypeOfReport:
    list_of_groups = get_list_of_groups(object_store)## will be ordered
    list_of_groups.add_unallocated()

    specific_parameters_for_allocation_report = SpecificParametersForTypeOfReport(
        #    entry_columns=[CADET_NAME],
        group_by_column=GROUP_NAME_COLUMN_HEADING_FOR_SPOTTER_SHEET,
        report_type="Rollcall report",
        group_order=list_of_groups.list_of_names(),
    unallocated_group = unallocated_group.name
    )

    return specific_parameters_for_allocation_report



@dataclass
class AdditionalParametersForRollcallReport:
    display_full_names: bool
    include_unallocated_cadets: bool
    add_asterix_for_club_boats: bool
    include_health_data: bool
    incude_emergency_contacts: bool

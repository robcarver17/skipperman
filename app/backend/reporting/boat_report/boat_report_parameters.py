from dataclasses import dataclass

from app.backend.groups.list_of_groups import get_list_of_groups
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.groups import unallocated_group

FIRST_CADET = "First cadet"
SECOND_CADET = "Second cadet"
GROUP = "Group"
BOAT_CLASS = "Boat class"
SAIL_NUMBER = "Sail number"
CLUB_BOAT = "Club boat"


def get_specific_parameters_for_boat_report(object_store: ObjectStore) -> SpecificParametersForTypeOfReport:
    list_of_groups = get_list_of_groups(object_store)## will be ordered
    list_of_groups.add_unallocated()
    specific_parameters_for_boat_report = SpecificParametersForTypeOfReport(
        #    entry_columns=[FIRST_CADET, SECOND_CADET, GROUP, BOAT_CLASS, SAIL_NUMBER, CLUB_BOAT],
        group_by_column=GROUP,
        report_type="Sailors with boats report",
        group_order=list_of_groups.list_of_names(),
        unallocated_group = unallocated_group.name
    )

    return specific_parameters_for_boat_report


@dataclass
class AdditionalParametersForBoatReport:
    display_full_names: bool
    exclude_lake_groups: bool
    exclude_river_training_groups: bool
    exclude_unallocated_groups: bool
    in_out_columns: bool

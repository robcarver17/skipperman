from dataclasses import dataclass
from app.OLD_backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)

FIRST_CADET = "First cadet"
SECOND_CADET = "Second cadet"
GROUP = "Group"
BOAT_CLASS = "Boat class"
SAIL_NUMBER = "Sail number"
CLUB_BOAT = "Club boat"

all_groups_names = []
specific_parameters_for_boat_report = SpecificParametersForTypeOfReport(
    #    entry_columns=[FIRST_CADET, SECOND_CADET, GROUP, BOAT_CLASS, SAIL_NUMBER, CLUB_BOAT],
    group_by_column=GROUP,
    passed_group_order=all_groups_names,
    report_type="Sailors with boats report",
)


@dataclass
class AdditionalParametersForBoatReport:
    display_full_names: bool
    exclude_lake_groups: bool
    exclude_river_training_groups: bool
    exclude_unallocated_groups: bool
    in_out_columns: bool

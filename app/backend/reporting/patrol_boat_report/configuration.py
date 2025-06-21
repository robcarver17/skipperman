from dataclasses import dataclass

from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)
from app.objects.patrol_boats import RIVER_SAFETY, LAKE_SAFETY
from app.data_access.store.object_store import ObjectStore
from app.objects.day_selectors import DaySelector

LOCATION = "Location"
VOLUNTEER = "Volunteer"
GROUP = "Group"
BOAT = "Boat"
DESIGNATION = "Designation"

LOCATIONS = [RIVER_SAFETY, LAKE_SAFETY]


def get_specific_parameters_for_patrol_boat_report(
    object_store: ObjectStore,
) -> SpecificParametersForTypeOfReport:
    specific_parameters_for_patrol_boat_report = SpecificParametersForTypeOfReport(
        group_by_column=LOCATION,
        report_type="Patrol boat report",
        group_order=LOCATIONS,
        unallocated_group="",
    )

    return specific_parameters_for_patrol_boat_report


@dataclass
class AdditionalParametersForPatrolBoatReport:
    days_to_show: DaySelector

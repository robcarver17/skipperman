from dataclasses import dataclass
from app.data_access.configuration.configuration import ALL_GROUPS_NAMES
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)

FOOD_GROUP_TYPE = "Type"
CADET_FOOD = "Cadet"
VOLUNTEER_FOOD = "Adult volunteer"
ADULT_FOOD = "Adult"
CHILD_FOOD = "Child"

ALL_TYPES = [CADET_FOOD, VOLUNTEER_FOOD, ADULT_FOOD, CHILD_FOOD]

specific_parameters_for_food_report = SpecificParametersForTypeOfReport(
    group_by_column=FOOD_GROUP_TYPE,
    passed_group_order=ALL_TYPES,
    report_type="Food required report"
)


@dataclass
class AdditionalParametersForFoodReport:
    include_cadets: bool
    include_volunteers: bool
    include_non_volunteer_adults: bool
    include_non_cadet_children: bool
    minimum_days_for_volunteer: int = 0
    
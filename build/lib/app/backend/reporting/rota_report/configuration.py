from dataclasses import dataclass

from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)
from app.objects.day_selectors import DaySelector

TEAM_NAME = "Team name"
ROLE = "Role"
VOLUNTEER = "Volunteer"
GROUP = "Group"
BOAT = "Boat"


specific_parameters_for_volunteer_report = SpecificParametersForTypeOfReport(
    #    entry_columns=[ROLE, VOLUNTEER, GROUP, BOAT],
    group_by_column=TEAM_NAME,
    report_type="Volunteer rota report",
)


@dataclass
class AdditionalParametersForVolunteerReport:
    days_to_show: DaySelector
    power_boats_only: bool = False

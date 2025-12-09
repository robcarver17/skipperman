from dataclasses import dataclass

from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.day_selectors import DaySelector
from app.backend.volunteers.roles_and_teams import get_list_of_teams
from app.objects.events import Event
from app.objects.roles_and_teams import no_team

TEAM_NAME = "Team name"
ROLE = "Role"
VOLUNTEER = "Volunteer"
GROUP = "Group"
BOAT = "Boat"


def get_specific_parameters_for_rota_report(
    object_store: ObjectStore,
        event: Event
) -> SpecificParametersForTypeOfReport:
    list_of_teams = get_list_of_teams(object_store)
    list_of_teams.add_unallocated()
    specific_parameters_for_rota_report = SpecificParametersForTypeOfReport(
        #    entry_columns=[ROLE, VOLUNTEER, GROUP, BOAT],
        group_by_column=TEAM_NAME,
        report_type="Volunteer rota report",
        group_order=list_of_teams.list_of_names(),
        unallocated_group=no_team.name,
    )

    return specific_parameters_for_rota_report


@dataclass
class AdditionalParametersForVolunteerReport:
    days_to_show: DaySelector

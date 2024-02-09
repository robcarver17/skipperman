from dataclasses import dataclass
from app.data_access.configuration.configuration import ALL_GROUPS_NAMES
from app.objects.groups import CADET_NAME, GROUP_STR_NAME
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)

specific_parameters_for_volunteer_report = SpecificParametersForTypeOfReport(
    entry_columns=[CADET_NAME],
    group_by_column=GROUP_STR_NAME,
    passed_group_order=ALL_GROUPS_NAMES,
    report_type="Volunteer rota report"
)


@dataclass
class AdditionalParametersForVolunteerReport:
    days_to_show: bool
    include_unallocated_cadets: bool


"""
What is the dataframe

Groups are Role, but we also want to sort by group

For instructors we ideally want a matrix

Need to know who leads are


"""
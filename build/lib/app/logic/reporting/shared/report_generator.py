from dataclasses import dataclass
from typing import Callable

from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)


@dataclass
class ReportGenerator:
    name: str
    event_criteria: dict
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport

    initial_display_form_function: Callable
    all_options_display_form_function: Callable

    print_options_display_form_function: Callable
    arrangement_options_display_form_function: Callable
    additional_options_display_form_function: Callable

    explain_additional_parameters: Callable
    load_additional_parameters: Callable
    clear_additional_parameters: Callable
    additional_parameters_form: Callable

    get_additional_parameters_from_form_and_save: Callable
    get_dict_of_df: Callable

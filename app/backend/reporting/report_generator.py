from dataclasses import dataclass
from typing import Callable

from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    SpecificParametersForTypeOfReport,
)
from app.data_access.store.object_store import ObjectStore


@dataclass
class ReportGenerator:
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

    @property
    def report_type(self):
        return self.specific_parameters_for_type_of_report.report_type


@dataclass
class ReportGeneratorWithoutSpecificParameters:
    event_criteria: dict
    specific_parameters_for_type_of_report_function: Callable

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

    def add_specific_parameters_for_type_of_report(
        self, object_store: ObjectStore
    ) -> ReportGenerator:
        specific_parameters = self.specific_parameters_for_type_of_report_function(
            object_store
        )
        return ReportGenerator(
            event_criteria=self.event_criteria,
            specific_parameters_for_type_of_report=specific_parameters,
            initial_display_form_function=self.initial_display_form_function,
            all_options_display_form_function=self.all_options_display_form_function,
            print_options_display_form_function=self.print_options_display_form_function,
            arrangement_options_display_form_function=self.arrangement_options_display_form_function,
            additional_options_display_form_function=self.additional_options_display_form_function,
            explain_additional_parameters=self.explain_additional_parameters,
            load_additional_parameters=self.load_additional_parameters,
            clear_additional_parameters=self.clear_additional_parameters,
            additional_parameters_form=self.additional_parameters_form,
            get_dict_of_df=self.get_dict_of_df,
            get_additional_parameters_from_form_and_save=self.get_additional_parameters_from_form_and_save,
        )

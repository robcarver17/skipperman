import pandas as pd
from typing import Dict, Callable

from app.backend.reporting.options_and_parameters.report_type_specific_parameters import \
    apply_override_additional_options
from app.backend.reporting.patrol_boat_report.configuration import (
    AdditionalParametersForPatrolBoatReport
)
from app.backend.reporting.patrol_boat_report.generate_data_for_patrol_boat_report import (
    get_df_for_reporting_patrol_boats_with_flags
)

from app.frontend.forms.form_utils import get_availablity_from_form
from app.backend.reporting.report_generator import ReportGenerator

from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.day_selectors import DaySelector
from app.objects.events import Event
from app.objects.utilities.exceptions import MISSING_FROM_FORM, arg_not_passed

DAYS_TO_SHOW = "DaysToShow"


def load_additional_parameters_for_patrol_boats_report(
    interface: abstractInterface,
) -> AdditionalParametersForPatrolBoatReport:
    days_to_show_str = interface.get_persistent_value(DAYS_TO_SHOW, None)
    if days_to_show_str is None:
        event = get_event_from_state(interface)
        days_to_show = event.day_selector_for_days_in_event()
    else:
        days_to_show = DaySelector.from_str(days_to_show_str)

    return AdditionalParametersForPatrolBoatReport(
        days_to_show=days_to_show
    )


def clear_additional_parameters_for_patrol_boats_report(
    interface: abstractInterface,
):
    interface.clear_persistent_value(DAYS_TO_SHOW)


def get_patrol_boats_report_additional_parameters_from_form_and_save(
    interface: abstractInterface,
    report_generator: ReportGenerator,  ## MUST BE INCLUDED AS ALWAYS PASSED
):
    parameters = get_patrol_boats_report_additional_parameters_from_form(interface)
    save_additional_parameters_for_patrol_boats_report(interface, parameters=parameters)


def get_patrol_boats_report_additional_parameters_from_form(
    interface: abstractInterface,
) -> AdditionalParametersForPatrolBoatReport:
    event = get_event_from_state(interface)
    days_to_show = get_availablity_from_form(
        event=event, interface=interface, input_name=DAYS_TO_SHOW
    )
    if days_to_show is MISSING_FROM_FORM:
        print("Days to show missing from form")
        days_to_show = event.day_selector_for_days_in_event()

    return AdditionalParametersForPatrolBoatReport(
        days_to_show=days_to_show
    )


def save_additional_parameters_for_patrol_boats_report(
    interface: abstractInterface, parameters: AdditionalParametersForPatrolBoatReport
):
    days_to_show_as_str = parameters.days_to_show.as_str()
    interface.set_persistent_value(DAYS_TO_SHOW, days_to_show_as_str)


def get_dict_of_df_for_reporting_patrol_boats(
    interface: abstractInterface,
        override_additional_options: dict = arg_not_passed

) -> Dict[str, pd.DataFrame]:
    event = get_event_from_state(interface)
    additional_parameters = load_additional_parameters_for_patrol_boats_report(interface)
    if override_additional_options is not arg_not_passed:
        additional_parameters=apply_override_additional_options(additional_parameters, **override_additional_options)

    dict_of_df = get_dict_of_df_for_reporting_patrol_boats_given_event_and_state(
        event=event, additional_parameters=additional_parameters, interface=interface
    )

    return dict_of_df


def get_dict_of_df_for_reporting_patrol_boats_given_event_and_state(
    interface: abstractInterface,
    event: Event,
    additional_parameters: AdditionalParametersForPatrolBoatReport,
) -> Dict[str, pd.DataFrame]:
    dict_of_df = get_df_for_reporting_patrol_boats_with_flags(
        object_store=interface.object_store,
        event=event,
        days_to_show=additional_parameters.days_to_show,
    )

    return dict_of_df


import pandas as pd
from typing import Dict

from app.backend.reporting.rota_report.configuration import (
    AdditionalParametersForVolunteerReport,
)
from app.backend.reporting.rota_report.generate_dataframe_dict_for_rota_report import (
    get_df_for_reporting_volunteers_with_flags,
)

from app.frontend.forms.form_utils import get_availablity_from_form

from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.day_selectors import DaySelector
from app.objects.events import Event


DAYS_TO_SHOW = "DaysToShow"
BOATS = "boats"


def load_additional_parameters_for_rota_report(
    interface: abstractInterface,
) -> AdditionalParametersForVolunteerReport:
    days_to_show_str = interface.get_persistent_value(DAYS_TO_SHOW, None)
    if days_to_show_str is None:
        event = get_event_from_state(interface)
        days_to_show = event.day_selector_with_covered_days()
    else:
        days_to_show = DaySelector.from_str(days_to_show_str)

    boats = interface.get_persistent_value(BOATS, default=False)
    return AdditionalParametersForVolunteerReport(
        days_to_show=days_to_show, power_boats_only=boats
    )


def clear_additional_parameters_for_rota_report(
    interface: abstractInterface,
):
    interface.clear_persistent_value(DAYS_TO_SHOW)
    interface.clear_persistent_value(BOATS)


def get_rota_report_additional_parameters_from_form_and_save(
    interface: abstractInterface,
):
    parameters = get_rota_report_additional_parameters_from_form(interface)
    save_additional_parameters_for_rota(interface, parameters=parameters)


def get_rota_report_additional_parameters_from_form(
    interface: abstractInterface,
) -> AdditionalParametersForVolunteerReport:
    event = get_event_from_state(interface)
    days_to_show = get_availablity_from_form(
        event=event, interface=interface, input_name=DAYS_TO_SHOW
    )

    boats = interface.true_if_radio_was_yes(BOATS)

    return AdditionalParametersForVolunteerReport(
        days_to_show=days_to_show, power_boats_only=boats
    )


def save_additional_parameters_for_rota(
    interface: abstractInterface, parameters: AdditionalParametersForVolunteerReport
):
    save_days_to_show_parameter(interface=interface, parameters=parameters)
    save_patrol_boat_parameter(interface=interface, parameters=parameters)


def save_days_to_show_parameter(
    interface: abstractInterface, parameters: AdditionalParametersForVolunteerReport
):
    days_to_show_as_str = parameters.days_to_show.as_str()
    interface.set_persistent_value(DAYS_TO_SHOW, days_to_show_as_str)


def save_patrol_boat_parameter(
    interface: abstractInterface, parameters: AdditionalParametersForVolunteerReport
):
    boats = parameters.power_boats_only
    interface.set_persistent_value(BOATS, boats)


def get_dict_of_df_for_reporting_rota(
    interface: abstractInterface,
) -> Dict[str, pd.DataFrame]:
    event = get_event_from_state(interface)
    additional_parameters = load_additional_parameters_for_rota_report(interface)

    dict_of_df = get_dict_of_df_for_reporting_rota_given_event_and_state(
        event=event, additional_parameters=additional_parameters, interface=interface
    )

    return dict_of_df


def get_dict_of_df_for_reporting_rota_given_event_and_state(
    interface: abstractInterface,
    event: Event,
    additional_parameters: AdditionalParametersForVolunteerReport,
) -> Dict[str, pd.DataFrame]:
    dict_of_df = get_df_for_reporting_volunteers_with_flags(
        object_store = interface.object_store,
        event=event,
        days_to_show=additional_parameters.days_to_show,
        power_boats_only=additional_parameters.power_boats_only,

    )

    return dict_of_df

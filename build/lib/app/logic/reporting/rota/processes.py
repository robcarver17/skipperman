import pandas as pd
from typing import Dict

from app.backend.reporting.process_stages.create_column_report_from_df import \
    create_column_report_from_df_and_return_filename
from app.backend.reporting.rota_report.configuration import AdditionalParametersForVolunteerReport, specific_parameters_for_volunteer_report
from app.backend.reporting.rota_report.generate_dataframe_dict_for_rota_report import get_df_for_reporting_volunteers_with_flags

from app.backend.forms.form_utils import get_availablity_from_form

from app.logic.events.events_in_state import get_event_from_state
from app.logic.reporting.shared.group_order import get_group_order_from_stored_or_df
from app.logic.reporting.shared.reporting_options import get_reporting_options
from app.objects.abstract_objects.abstract_form import File
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.day_selectors import DaySelector
from app.objects.events import Event



DAYS_TO_SHOW = "DaysToShow"

def load_additional_parameters_for_rota_report(
    interface: abstractInterface,
) -> AdditionalParametersForVolunteerReport:
    days_to_show_str = interface.get_persistent_value(DAYS_TO_SHOW, None)
    if days_to_show_str is None:
        event = get_event_from_state(interface)
        days_to_show = event.day_selector_with_covered_days()
    else:
        days_to_show = DaySelector.from_str(days_to_show_str)

    return AdditionalParametersForVolunteerReport(
        days_to_show=days_to_show
    )


def get_rota_report_additional_parameters_from_form_and_save(
    interface: abstractInterface,
):
    parameters = get_rota_report_additional_parameters_from_form(interface)
    save_additional_parameters_for_rota(interface, parameters=parameters)


def get_rota_report_additional_parameters_from_form(
    interface: abstractInterface,
) -> AdditionalParametersForVolunteerReport:
    event = get_event_from_state(interface)
    days_to_show = get_availablity_from_form(event=event,
                                             interface=interface,
                                             input_name=DAYS_TO_SHOW)

    return AdditionalParametersForVolunteerReport(
        days_to_show=days_to_show)


def save_additional_parameters_for_rota(
    interface: abstractInterface, parameters: AdditionalParametersForVolunteerReport
):
    save_days_to_show_parameter(interface=interface, parameters=parameters)


def save_days_to_show_parameter(interface: abstractInterface, parameters: AdditionalParametersForVolunteerReport):
    days_to_show_as_str = parameters.days_to_show.as_str()
    interface.set_persistent_value(DAYS_TO_SHOW, days_to_show_as_str)


def get_dict_of_df_for_reporting_rota(interface: abstractInterface) -> Dict[str, pd.DataFrame]:
    event = get_event_from_state(interface)
    additional_parameters = load_additional_parameters_for_rota_report(interface)

    dict_of_df = get_dict_of_df_for_reporting_rota_given_event_and_state(

        event=event,
        additional_parameters=additional_parameters
    )

    return dict_of_df

def get_dict_of_df_for_reporting_rota_given_event_and_state(event: Event, additional_parameters: AdditionalParametersForVolunteerReport)->  Dict[str, pd.DataFrame]:
    dict_of_df = get_df_for_reporting_volunteers_with_flags(
        event=event,
        days_to_show=additional_parameters.days_to_show
    )

    return dict_of_df



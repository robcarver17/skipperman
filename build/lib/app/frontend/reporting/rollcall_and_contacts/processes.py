from typing import Dict, Callable

from app.backend.reporting import report_generator
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import (
    apply_override_additional_options,
)
from app.backend.reporting.rollcall_report.get_data import (
    get_dict_of_df_for_reporting_rollcalls_given_event_and_parameters,
)
import pandas as pd

from app.backend.reporting.report_generator import ReportGenerator
from app.frontend.reporting.shared.arrangement_state import (
    reset_arrangement_to_default_with_groups_in_data,
)
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.reporting.rollcall_report.configuration import (
    AdditionalParametersForRollcallReport,
)
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.utilities.transform_data import from_bool_to_str, TRUE, from_str_to_bool


def get_group_rollcall_report_additional_parameters_from_form_and_save(
    interface: abstractInterface, report_generator: ReportGenerator
):
    parameters = get_group_rollcall_report_additional_parameters_from_form(interface)
    save_additional_parameters_for_rollcall(
        interface, parameters=parameters, report_generator=report_generator
    )


def get_group_rollcall_report_additional_parameters_from_form(
    interface: abstractInterface,
) -> AdditionalParametersForRollcallReport:
    display_full_names = interface.true_if_radio_was_yes(SHOW_FULL_NAMES)
    include_unallocated_cadets = interface.true_if_radio_was_yes(
        INCLUDE_UNALLOCATED_CADETS
    )
    add_asterix_for_club_boats = interface.true_if_radio_was_yes(CLUB_BOAT_ASTERIX)
    include_health_data = interface.true_if_radio_was_yes(HEALTH_DATA)
    include_emergency_contacts = interface.true_if_radio_was_yes(EMERGENCY_CONTACTS)

    return AdditionalParametersForRollcallReport(
        display_full_names=display_full_names,
        include_unallocated_cadets=include_unallocated_cadets,
        add_asterix_for_club_boats=add_asterix_for_club_boats,
        incude_emergency_contacts=include_emergency_contacts,
        include_health_data=include_health_data,
    )


def save_additional_parameters_for_rollcall(
    interface: abstractInterface,
    parameters: AdditionalParametersForRollcallReport,
    report_generator: ReportGenerator,
):
    save_show_full_names_parameter(interface=interface, parameters=parameters)
    save_club_boat_asterix_parameter(interface=interface, parameters=parameters)
    save_emergency_contact_parameter(interface=interface, parameters=parameters)
    save_include_health_details_parameter(interface=interface, parameters=parameters)
    save_unallocated_parameter(
        interface=interface, parameters=parameters, report_generator=report_generator
    )


def save_show_full_names_parameter(
    interface: abstractInterface, parameters: AdditionalParametersForRollcallReport
):
    interface.set_persistent_value(SHOW_FULL_NAMES, from_bool_to_str(parameters.display_full_names))


def save_club_boat_asterix_parameter(
    interface: abstractInterface, parameters: AdditionalParametersForRollcallReport
):
    interface.set_persistent_value(
        CLUB_BOAT_ASTERIX, from_bool_to_str(parameters.add_asterix_for_club_boats
    ))


def save_unallocated_parameter(
    interface: abstractInterface,
    parameters: AdditionalParametersForRollcallReport,
    report_generator: ReportGenerator,
):
    unallocated_parameter_has_changed = has_unallocated_parameter_changed(
        interface=interface, parameters=parameters
    )
    interface.set_persistent_value(
        INCLUDE_UNALLOCATED_CADETS, from_bool_to_str(parameters.include_unallocated_cadets)
    )

    if unallocated_parameter_has_changed:
        interface.log_error(
            "Exclude unallocated sailor settings have changed - resetting arrangement"
        )
        reset_arrangement_to_default_with_groups_in_data(
            interface=interface, report_generator=report_generator
        )


def has_unallocated_parameter_changed(
    interface: abstractInterface, parameters: AdditionalParametersForRollcallReport
):
    current_parameters = load_additional_parameters_for_rollcall_report(interface)
    current_unalloacted_parameter = current_parameters.include_unallocated_cadets
    new_unalloacted_parameter = parameters.include_unallocated_cadets

    return current_unalloacted_parameter != new_unalloacted_parameter


def save_emergency_contact_parameter(
    interface: abstractInterface, parameters: AdditionalParametersForRollcallReport
):
    interface.set_persistent_value(
        EMERGENCY_CONTACTS, from_bool_to_str(parameters.incude_emergency_contacts
    ))


def save_include_health_details_parameter(
    interface: abstractInterface, parameters: AdditionalParametersForRollcallReport
):
    interface.set_persistent_value(HEALTH_DATA, from_bool_to_str(parameters.include_health_data))


def load_additional_parameters_for_rollcall_report(
    interface: abstractInterface,
) -> AdditionalParametersForRollcallReport:
    display_full_names = interface.get_persistent_value(SHOW_FULL_NAMES, TRUE)
    display_full_names = from_str_to_bool(display_full_names)

    include_unallocated_cadets = interface.get_persistent_value(
        INCLUDE_UNALLOCATED_CADETS, TRUE
    )
    include_unallocated_cadets = from_str_to_bool(include_unallocated_cadets)

    add_asterix_for_club_boats = interface.get_persistent_value(CLUB_BOAT_ASTERIX, TRUE)
    add_asterix_for_club_boats = from_str_to_bool(add_asterix_for_club_boats)

    include_health_data = interface.get_persistent_value(HEALTH_DATA, TRUE)
    include_health_data = from_str_to_bool(include_health_data)

    include_emergency_contacts = interface.get_persistent_value(
        EMERGENCY_CONTACTS, TRUE
    )
    include_emergency_contacts = from_str_to_bool(include_emergency_contacts)

    return AdditionalParametersForRollcallReport(
        display_full_names=display_full_names,
        include_unallocated_cadets=include_unallocated_cadets,
        add_asterix_for_club_boats=add_asterix_for_club_boats,
        include_health_data=include_health_data,
        incude_emergency_contacts=include_emergency_contacts,
    )


def clear_additional_parameters_for_rollcall_report(
    interface: abstractInterface,
):
    for parameter_name in [
        SHOW_FULL_NAMES,
        INCLUDE_UNALLOCATED_CADETS,
        CLUB_BOAT_ASTERIX,
        HEALTH_DATA,
        EMERGENCY_CONTACTS,
    ]:
        interface.clear_persistent_value(parameter_name)


def get_dict_of_df_for_reporting_rollcalls(
    interface: abstractInterface, override_additional_options: dict = arg_not_passed
) -> Dict[str, pd.DataFrame]:
    event = get_event_from_state(interface)
    additional_parameters = load_additional_parameters_for_rollcall_report(interface)
    if override_additional_options is not arg_not_passed:
        additional_parameters = apply_override_additional_options(
            additional_parameters, **override_additional_options
        )

    dict_of_df = get_dict_of_df_for_reporting_rollcalls_given_event_and_parameters(
        object_store=interface.object_store,
        event=event,
        additional_parameters=additional_parameters,
    )

    return dict_of_df


SHOW_FULL_NAMES = "Show_full_names"
INCLUDE_UNALLOCATED_CADETS = "Include unallocated group rollcalls"
CLUB_BOAT_ASTERIX = "Asterix for club boats"
HEALTH_DATA = "Include confidential health data"
EMERGENCY_CONTACTS = "Include private emergency contact names and phone numbers"

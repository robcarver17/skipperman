from typing import Union

from app.frontend.reporting.patrol_boats.forms import (
    reporting_options_form_for_patrol_boats_additional_parameters,
    explain_additional_parameters_for_patrol_boats_report,
)
from app.frontend.reporting.patrol_boats.processes import (
    get_dict_of_df_for_reporting_patrol_boats,
    load_additional_parameters_for_patrol_boats_report,
    clear_additional_parameters_for_patrol_boats_report,
    get_patrol_boats_report_additional_parameters_from_form_and_save,
)


from app.frontend.reporting.shared.generic_report_pages import (
    post_form_initial_generic_report,
    post_form_for_generic_report_arrangement_options,
    display_form_for_generic_report_all_options,
    post_form_for_generic_report_all_options,
    display_form_for_generic_report_additional_options,
    post_form_for_generic_report_additional_options,
    display_form_for_generic_report_print_options,
    post_form_for_generic_report_print_options,
    display_form_for_generic_report_arrangement_options,
    display_initial_generic_report_form,
)
from app.backend.reporting.report_generator import (
    ReportGeneratorWithoutSpecificParameters,
)

from app.backend.reporting.patrol_boat_report.configuration import (
    get_specific_parameters_for_patrol_boat_report,
)

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface


def display_form_report_patrol_boats(interface: abstractInterface) -> Form:
    return display_initial_generic_report_form(
        interface=interface, report_generator=patrol_boat_report_generator
    )


def post_form_report_patrol_boats(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return post_form_initial_generic_report(
        interface=interface, report_generator=patrol_boat_report_generator
    )


# GENERIC_OPTIONS_IN_ROTA_REPORT_STATE
def display_form_for_patrol_boats_all_options(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return display_form_for_generic_report_all_options(
        interface=interface, report_generator=patrol_boat_report_generator
    )


def post_form_for_patrol_boats_report_all_options(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    return post_form_for_generic_report_all_options(
        interface=interface, report_generator=patrol_boat_report_generator
    )


# REPORT_ADDITIONAL_OPTIONS_FOR_ROTA_REPORT_STATE
def display_form_for_patrol_boats_additional_options(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return display_form_for_generic_report_additional_options(
        interface=interface, report_generator=patrol_boat_report_generator
    )


# REPORT_ADDITIONAL_OPTIONS_FOR_ROTA_REPORT_STATE
def post_form_for_patrol_boats_report_additional_options(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    return post_form_for_generic_report_additional_options(
        interface=interface, report_generator=patrol_boat_report_generator
    )


# CHANGE_PRINT_OPTIONS_IN_ROTA_REPORT_STATE
def display_form_for_patrol_boats_report_print_options(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return display_form_for_generic_report_print_options(
        interface=interface, report_generator=patrol_boat_report_generator
    )


# CHANGE_PRINT_OPTIONS_IN_ROTA_REPORT_STATE
def post_form_for_patrol_boats_report_print_options(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    return post_form_for_generic_report_print_options(
        interface=interface, report_generator=patrol_boat_report_generator
    )


# CHANGE_GROUP_LAYOUT_IN_ROTA_REPORT_STATE
def display_form_for_patrol_boats_arrangement_options_report(
    interface: abstractInterface,
) -> Form:
    return display_form_for_generic_report_arrangement_options(
        interface=interface, report_generator=patrol_boat_report_generator
    )


# CHANGE_GROUP_LAYOUT_IN_ROTA_REPORT_STATE
def post_form_for_group_arrangement_options_patrol_boats_report(
    interface: abstractInterface,
) -> Union[NewForm, Form, File]:
    return post_form_for_generic_report_arrangement_options(
        interface=interface, report_generator=patrol_boat_report_generator
    )


patrol_boat_report_generator = ReportGeneratorWithoutSpecificParameters(
    event_criteria=dict(requires_volunteers=True),
    specific_parameters_for_type_of_report_function=get_specific_parameters_for_patrol_boat_report,
    initial_display_form_function=display_form_report_patrol_boats,
    all_options_display_form_function=display_form_for_patrol_boats_all_options,
    additional_options_display_form_function=display_form_for_patrol_boats_additional_options,
    arrangement_options_display_form_function=display_form_for_patrol_boats_arrangement_options_report,
    print_options_display_form_function=display_form_for_patrol_boats_report_print_options,
    get_dict_of_df=get_dict_of_df_for_reporting_patrol_boats,
    load_additional_parameters=load_additional_parameters_for_patrol_boats_report,
    clear_additional_parameters=clear_additional_parameters_for_patrol_boats_report,
    explain_additional_parameters=explain_additional_parameters_for_patrol_boats_report,
    additional_parameters_form=reporting_options_form_for_patrol_boats_additional_parameters,
    get_additional_parameters_from_form_and_save=get_patrol_boats_report_additional_parameters_from_form_and_save,
    help_page="patrol_boats_rota_report_help",
)

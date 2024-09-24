from typing import Union

from app.frontend.reporting.boats.forms import (
    reporting_options_form_for_boat_additional_parameters,
    explain_additional_parameters_for_boat_report,
)
from app.frontend.reporting.boats.processes import (
    get_dict_of_df_for_reporting_boats,
    load_additional_parameters_for_boat_report,
    get_boat_allocation_report_additional_parameters_from_form_and_save,
    clear_additional_parameters_for_boat_report,
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
from app.frontend.reporting.shared.report_generator import ReportGenerator

from app.OLD_backend.reporting.boat_report.boat_report_parameters import (
    specific_parameters_for_boat_report,
)

from app.objects_OLD.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects_OLD.abstract_objects.abstract_interface import abstractInterface


def display_form_report_boat(interface: abstractInterface) -> Form:
    return display_initial_generic_report_form(
        interface=interface, report_generator=boat_report_generator
    )


def post_form_report_boat(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return post_form_initial_generic_report(
        interface=interface, report_generator=boat_report_generator
    )


# GENERIC_OPTIONS_IN_boat_REPORT_STATE
def display_form_for_boat_report_all_options(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return display_form_for_generic_report_all_options(
        interface=interface, report_generator=boat_report_generator
    )


def post_form_for_boat_report_all_options(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    return post_form_for_generic_report_all_options(
        interface=interface, report_generator=boat_report_generator
    )


# REPORT_ADDITIONAL_OPTIONS_FOR_boat_REPORT_STATE
def display_form_for_boat_report_additional_options(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return display_form_for_generic_report_additional_options(
        interface=interface, report_generator=boat_report_generator
    )


# REPORT_ADDITIONAL_OPTIONS_FOR_boat_REPORT_STATE
def post_form_for_boat_report_additional_options(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    return post_form_for_generic_report_additional_options(
        interface=interface, report_generator=boat_report_generator
    )


# CHANGE_PRINT_OPTIONS_IN_boat_REPORT_STATE
def display_form_for_boat_report_print_options(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return display_form_for_generic_report_print_options(
        interface=interface, report_generator=boat_report_generator
    )


# CHANGE_PRINT_OPTIONS_IN_boat_REPORT_STATE
def post_form_for_boat_report_print_options(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    return post_form_for_generic_report_print_options(
        interface=interface, report_generator=boat_report_generator
    )


# CHANGE_GROUP_LAYOUT_IN_boat_REPORT_STATE
def display_form_for_group_arrangement_options_boat_report(
    interface: abstractInterface,
) -> Form:
    return display_form_for_generic_report_arrangement_options(
        interface=interface, report_generator=boat_report_generator
    )


# CHANGE_GROUP_LAYOUT_IN_boat_REPORT_STATE
def post_form_for_group_arrangement_options_boat_report(
    interface: abstractInterface,
) -> Union[NewForm, Form, File]:
    return post_form_for_generic_report_arrangement_options(
        interface=interface, report_generator=boat_report_generator
    )


boat_report_generator = ReportGenerator(
    name="Boats and sailors spotters report",
    event_criteria=dict(requires_cadets_and_boats=True),
    specific_parameters_for_type_of_report=specific_parameters_for_boat_report,
    initial_display_form_function=display_form_report_boat,
    all_options_display_form_function=display_form_for_boat_report_all_options,
    additional_options_display_form_function=display_form_for_boat_report_additional_options,
    arrangement_options_display_form_function=display_form_for_group_arrangement_options_boat_report,
    print_options_display_form_function=display_form_for_boat_report_print_options,
    get_dict_of_df=get_dict_of_df_for_reporting_boats,
    load_additional_parameters=load_additional_parameters_for_boat_report,
    clear_additional_parameters=clear_additional_parameters_for_boat_report,
    explain_additional_parameters=explain_additional_parameters_for_boat_report,
    additional_parameters_form=reporting_options_form_for_boat_additional_parameters,
    get_additional_parameters_from_form_and_save=get_boat_allocation_report_additional_parameters_from_form_and_save,
)

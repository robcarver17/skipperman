from typing import Union

from app.frontend.reporting.allocations.forms import (
    reporting_options_form_for_group_additional_parameters,
    explain_additional_parameters_for_allocation_report,
)
from app.frontend.reporting.allocations.processes import (
    get_group_allocation_report_additional_parameters_from_form_and_save,
    get_dict_of_df_for_reporting_allocations,
    load_additional_parameters_for_allocation_report,
    clear_additional_parameters_for_allocation_report,
)
from app.frontend.reporting.shared.generic_report_pages import (
    display_initial_generic_report_form,
    post_form_initial_generic_report,
    display_form_for_generic_report_all_options,
    post_form_for_generic_report_all_options,
    display_form_for_generic_report_additional_options,
    post_form_for_generic_report_additional_options,
    display_form_for_generic_report_print_options,
    post_form_for_generic_report_print_options,
    post_form_for_generic_report_arrangement_options,
    display_form_for_generic_report_arrangement_options,
)
from app.backend.reporting.report_generator import (
    ReportGeneratorWithoutSpecificParameters,
)

from app.backend.reporting.allocation_report.allocation_report import (
    get_specific_parameters_for_allocation_report,
)

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface


# GROUP_ALLOCATION_REPORT_STAGE
def display_form_report_group_allocation(interface: abstractInterface) -> Form:
    return display_initial_generic_report_form(
        interface=interface, report_generator=allocation_report_generator
    )


def post_form_report_group_allocation(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return post_form_initial_generic_report(
        interface=interface, report_generator=allocation_report_generator
    )


# GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE
def display_form_for_report_group_allocation_all_options(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return display_form_for_generic_report_all_options(
        interface=interface, report_generator=allocation_report_generator
    )


def post_form_for_report_group_allocation_all_options(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    return post_form_for_generic_report_all_options(
        interface=interface, report_generator=allocation_report_generator
    )


# REPORT_ADDITIONAL_OPTIONS_FOR_ALLOCATION_REPORT
def display_form_for_report_group_additional_options(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return display_form_for_generic_report_additional_options(
        interface=interface, report_generator=allocation_report_generator
    )


def post_form_for_report_group_additional_options(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    return post_form_for_generic_report_additional_options(
        interface=interface, report_generator=allocation_report_generator
    )


# CHANGE_PRINT_OPTIONS_IN_GROUP_ALLOCATION_STATE
def display_form_for_report_group_allocation_print_options(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return display_form_for_generic_report_print_options(
        interface=interface, report_generator=allocation_report_generator
    )


def post_form_for_report_group_allocation_print_options(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    return post_form_for_generic_report_print_options(
        interface=interface, report_generator=allocation_report_generator
    )


# CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE
def display_form_for_group_arrangement_options_allocation_report(
    interface: abstractInterface,
) -> Form:
    return display_form_for_generic_report_arrangement_options(
        interface=interface, report_generator=allocation_report_generator
    )


def post_form_for_group_arrangement_options_allocation_report(
    interface: abstractInterface,
) -> Union[NewForm, Form, File]:
    return post_form_for_generic_report_arrangement_options(
        interface=interface, report_generator=allocation_report_generator
    )


allocation_report_generator = ReportGeneratorWithoutSpecificParameters(
    event_criteria=dict(requires_group_allocations=True),
    specific_parameters_for_type_of_report_function=get_specific_parameters_for_allocation_report,
    initial_display_form_function=display_form_report_group_allocation,
    all_options_display_form_function=display_form_for_report_group_allocation_all_options,
    additional_options_display_form_function=display_form_for_report_group_additional_options,
    arrangement_options_display_form_function=display_form_for_group_arrangement_options_allocation_report,
    print_options_display_form_function=display_form_for_report_group_allocation_print_options,
    get_dict_of_df=get_dict_of_df_for_reporting_allocations,
    load_additional_parameters=load_additional_parameters_for_allocation_report,
    clear_additional_parameters=clear_additional_parameters_for_allocation_report,
    explain_additional_parameters=explain_additional_parameters_for_allocation_report,
    additional_parameters_form=reporting_options_form_for_group_additional_parameters,
    get_additional_parameters_from_form_and_save=get_group_allocation_report_additional_parameters_from_form_and_save,
    help_page='group_allocation_report_help'
)

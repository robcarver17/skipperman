from typing import Union

from app.logic.reporting.allocations.forms import (
    reporting_options_form_for_group_additional_parameters,
    get_text_explaining_various_options_for_allocations_report,
)
from app.logic.reporting.allocations.processes import (
    get_group_allocation_report_additional_parameters_from_form_and_save,
    get_df_for_reporting_allocations,
    create_report
)
from app.logic.reporting.options.arrangement_form import form_for_group_arrangement_options, \
    post_form_for_group_arrangement_options
from app.logic.reporting.options.print_options import (
    save_print_options,
    get_print_options_from_main_option_form_fields,
    get_saved_print_options_and_create_form,
)

from app.backend.reporting.allocation_report import specific_parameters_for_allocation_report

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects.abstract_objects.abstract_text import bold
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL, CANCEL_BUTTON_LABEL, Button
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import initial_state_form, button_error_and_back_to_initial_state_form
from app.logic.events.events_in_state import get_event_from_state, update_state_for_specific_event_given_event_description
from app.backend.events import confirm_event_exists_given_description

from app.logic.reporting.constants import *
from app.logic.events.ENTRY_view_events import display_list_of_events_with_buttons


# GROUP_ALLOCATION_REPORT_STAGE
def display_form_report_group_allocation(interface: abstractInterface) -> Form:
    list_of_events = display_list_of_events_with_buttons()
    lines_inside_form = ListOfLines(
        [back_button, _______________, "Select event:", _______________, list_of_events]
    )

    return Form(lines_inside_form)

back_button = Button(BACK_BUTTON_LABEL)

def post_form_report_group_allocation(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    last_button = interface.last_button_pressed()
    if last_button == BACK_BUTTON_LABEL:
        return initial_state_form

    event_name_selected = last_button
    try:
        confirm_event_exists_given_description(event_name_selected)
    except:
        interface.log_error(
            "Event %s no longer in list- someone else has deleted or file corruption?"
            % event_name_selected
        )
        return initial_state_form

    ## so whilst we are in this stage, we know which event we are talking about
    update_state_for_specific_event_given_event_description(
        interface=interface, event_description=event_name_selected
    )

    return NewForm(GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE)


# GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE
def display_form_for_report_group_allocation_generic_options(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    (
        additional_options_as_text,
        print_options_as_text,
        arrangement_and_order_text,
    ) = get_text_explaining_various_options_for_allocations_report(interface)

    return Form(
        ListOfLines(
            [
                cancel_button,
                back_button,
                _______________,
                bold("Allocation report: Select reporting options for %s" % str(event)),
                _______________,
                additional_options_as_text,
                Button(MODIFY_ADDITIONAL_OPTIONS_BUTTON_LABEL),
                _______________,
                print_options_as_text,
                Button(MODIFY_PRINT_OPTIONS_BUTTON_LABEL),
                _______________,
                arrangement_and_order_text,
                Button(CHANGE_GROUP_LAYOUT_BUTTON),
                _______________,
                Button(CREATE_REPORT_BUTTON_LABEL),
            ]
        )
    )

cancel_button = Button(CANCEL_BUTTON_LABEL)

def post_form_for_report_group_allocation_generic_options(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed == CREATE_REPORT_BUTTON_LABEL:
        return create_report(interface)

    elif last_button_pressed == MODIFY_PRINT_OPTIONS_BUTTON_LABEL:
        return NewForm(CHANGE_PRINT_OPTIONS_IN_GROUP_ALLOCATION_STATE)

    elif last_button_pressed == CHANGE_GROUP_LAYOUT_BUTTON:
        return NewForm(CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE)

    elif last_button_pressed == MODIFY_ADDITIONAL_OPTIONS_BUTTON_LABEL:
        return NewForm(REPORT_ADDITIONAL_OPTIONS_FOR_ALLOCATION_REPORT)

    elif last_button_pressed == BACK_BUTTON_LABEL:
        # otherwise event/report specific data like filenames is remembered; also group order which could break everything if persisted
        # note if the report type was persistently stored we'd need to keep it here but it is not
        interface.clear_persistent_data_except_specified_fields([])
        return NewForm(GROUP_ALLOCATION_REPORT_STAGE)
    elif last_button_pressed == CANCEL_BUTTON_LABEL:
        return initial_state_form
    else:
        button_error_and_back_to_initial_state_form(interface)

# REPORT_ADDITIONAL_OPTIONS_FOR_ALLOCATION_REPORT
def display_form_for_report_group_additional_options(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    reporting_options_this_report = (
        reporting_options_form_for_group_additional_parameters(interface)
    )
    return Form(
        ListOfLines(
            [
                cancel_button,
                back_button,
                _______________,
                "Allocation report: Select reporting options for %s" % str(event),
                _______________,
                reporting_options_this_report,
                _______________,
                Line([Button(SAVE_THESE_OPTIONS_BUTTON_LABEL), Button(CREATE_REPORT_BUTTON_LABEL)])
            ]
        )
    )


def post_form_for_report_group_allocation_options(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed == BACK_BUTTON_LABEL:
        return NewForm(GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE)
    elif  last_button_pressed== CREATE_REPORT_BUTTON_LABEL:
        get_group_allocation_report_additional_parameters_from_form_and_save(interface)
        return create_report(interface)
    elif last_button_pressed == SAVE_THESE_OPTIONS_BUTTON_LABEL:
        get_group_allocation_report_additional_parameters_from_form_and_save(interface)
        return NewForm(GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE)
    elif last_button_pressed == CANCEL_BUTTON_LABEL:
        return initial_state_form
    else:
        button_error_and_back_to_initial_state_form(interface)


# CHANGE_PRINT_OPTIONS_IN_GROUP_ALLOCATION_STATE
def display_form_for_report_group_allocation_print_options(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    form_of_print_options = get_saved_print_options_and_create_form(
        interface=interface, report_type=specific_parameters_for_allocation_report.report_type, report_for=str(event)
    )

    return Form(
        ListOfLines(
            [
                cancel_button,
                _______________,
                form_of_print_options,
                _______________,
                Line(
                    [
                        back_button,
                        Button(SAVE_THESE_OPTIONS_BUTTON_LABEL),
                        Button(CREATE_REPORT_BUTTON_LABEL),
                    ]
                ),
            ]
        )
    )


def post_form_for_report_group_allocation_print_options(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()

    if last_button_pressed == BACK_BUTTON_LABEL:
        return NewForm(GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE)
    elif last_button_pressed == CANCEL_BUTTON_LABEL:
        return initial_state_form

    print_options = get_print_options_from_main_option_form_fields(interface)
    save_print_options(
        report_type=specific_parameters_for_allocation_report.report_type, print_options=print_options, interface=interface
    )
    if last_button_pressed == CREATE_REPORT_BUTTON_LABEL:
        return create_report(interface)
    elif last_button_pressed == SAVE_THESE_OPTIONS_BUTTON_LABEL:
        return NewForm(GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE)
    else:
        return button_error_and_back_to_initial_state_form(interface)


# CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE
def display_form_for_group_arrangement_options_allocation_report(interface: abstractInterface) -> Form:
    df = get_df_for_reporting_allocations(interface)

    form_for_arrangement_options = form_for_group_arrangement_options(interface=interface,
                                                                      df=df,
                                                                      specific_parameters_for_type_of_report=specific_parameters_for_allocation_report)

    return Form(
        ListOfLines(
            [
                cancel_button,
                form_for_arrangement_options,
                _______________,
                Line([back_button, Button(CREATE_REPORT_BUTTON_LABEL)]),
            ]
        )
    )



def post_form_for_group_arrangement_options_allocation_report(
        interface: abstractInterface,
) -> Union[NewForm, Form, File]:
    last_button_pressed = interface.last_button_pressed()

    if last_button_pressed == CREATE_REPORT_BUTTON_LABEL:
        return create_report(interface)
    elif last_button_pressed == BACK_BUTTON_LABEL:
        return NewForm(GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE)
    elif last_button_pressed == CANCEL_BUTTON_LABEL:
        return initial_state_form
    else:
        ## Changing arrangement
        df = get_df_for_reporting_allocations(interface)
        return post_form_for_group_arrangement_options(interface=interface,
                                                       current_form_name=CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE,
                                                       df=df,
                                                       specific_parameters_for_type_of_report=specific_parameters_for_allocation_report)




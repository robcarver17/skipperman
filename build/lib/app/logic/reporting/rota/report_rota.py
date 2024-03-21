from typing import Union

from app.logic.reporting.shared.event_lists import display_list_of_events_with_buttons_criteria_matched
from app.logic.reporting.rota.forms import reporting_options_form_for_rota_additional_parameters
from app.logic.reporting.rota.processes import get_dict_of_df_for_reporting_rota, create_rota_report

from app.logic.reporting.rota.processes import get_rota_report_additional_parameters_from_form_and_save

from app.logic.reporting.shared.arrangement_form import form_for_group_arrangement_options, \
    post_form_for_group_arrangement_options
from app.logic.reporting.shared.print_options import (
    save_print_options,
    get_print_options_from_main_option_form_fields,
    get_saved_print_options_and_create_form,
)

from app.backend.reporting.rota_report.configuration import specific_parameters_for_volunteer_report
from app.logic.reporting.rota.forms import get_text_explaining_various_options_for_rota_report

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


def display_form_report_rota(interface: abstractInterface) -> Form:
    list_of_events = (
        display_list_of_events_with_buttons_criteria_matched(
            requires_volunteers=True
    ))
    lines_inside_form = ListOfLines(
        [back_button, _______________, "Select event (only includes events with volunteers in rota):", _______________, list_of_events]
    )

    return Form(lines_inside_form)

back_button = Button(BACK_BUTTON_LABEL)

def post_form_report_rota(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    last_button = interface.last_button_pressed()
    if last_button == BACK_BUTTON_LABEL:
        return interface.get_new_display_form_for_parent_of_function(display_form_report_rota)

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

    return interface.get_new_form_given_function(display_form_for_rota_report_generic_options)


# GENERIC_OPTIONS_IN_ROTA_REPORT_STATE
def display_form_for_rota_report_generic_options(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    (
        additional_options_as_text,
        print_options_as_text,
        arrangement_and_order_text,
    ) = get_text_explaining_various_options_for_rota_report(interface)

    return Form(
        ListOfLines(
            [
                cancel_button,
                back_button,
                _______________,
                bold("Volunteer rota report: Select reporting shared for %s" % str(event)),
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

#GENERIC_OPTIONS_IN_ROTA_REPORT_STATE
def post_form_for_rota_report_generic_options(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed == CREATE_REPORT_BUTTON_LABEL:
        return create_rota_report(interface)

    elif last_button_pressed == MODIFY_PRINT_OPTIONS_BUTTON_LABEL:
        return interface.get_new_form_given_function(display_form_for_rota_report_print_options)

    elif last_button_pressed == CHANGE_GROUP_LAYOUT_BUTTON:
        return interface.get_new_form_given_function(display_form_for_group_arrangement_options_rota_report)

    elif last_button_pressed == MODIFY_ADDITIONAL_OPTIONS_BUTTON_LABEL:
        return interface.get_new_form_given_function(display_form_for_rota_report_additional_options)

    elif last_button_pressed == BACK_BUTTON_LABEL:
        # otherwise event/report specific data like filenames is remembered; also group order which could break everything if persisted
        # note if the report type was persistently stored we'd need to keep it here but it is not
        interface.clear_persistent_data_except_specified_fields([])
        return interface.get_new_display_form_for_parent_of_function(display_form_for_rota_report_generic_options)

    elif last_button_pressed == CANCEL_BUTTON_LABEL:
        return initial_state_form
    else:
        button_error_and_back_to_initial_state_form(interface)

# REPORT_ADDITIONAL_OPTIONS_FOR_ROTA_REPORT_STATE
def display_form_for_rota_report_additional_options(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    reporting_options_this_report = (
        reporting_options_form_for_rota_additional_parameters(interface)
    )
    return Form(
        ListOfLines(
            [
                cancel_button,
                back_button,
                _______________,
                "Volunteer rota report: Select reporting shared for %s" % str(event),
                _______________,
                reporting_options_this_report,
                _______________,
                Line([Button(SAVE_THESE_OPTIONS_BUTTON_LABEL), Button(CREATE_REPORT_BUTTON_LABEL)])
            ]
        )
    )


# REPORT_ADDITIONAL_OPTIONS_FOR_ROTA_REPORT_STATE
def post_form_for_rota_report_additional_options(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()
    previous_form = interface.get_new_display_form_for_parent_of_function(display_form_for_rota_report_additional_options)

    if last_button_pressed == BACK_BUTTON_LABEL:
        return previous_form

    elif  last_button_pressed== CREATE_REPORT_BUTTON_LABEL:
        get_rota_report_additional_parameters_from_form_and_save(interface)
        return create_rota_report(interface)

    elif last_button_pressed == SAVE_THESE_OPTIONS_BUTTON_LABEL:
        get_rota_report_additional_parameters_from_form_and_save(interface)
        return previous_form

    elif last_button_pressed == CANCEL_BUTTON_LABEL:
        return initial_state_form

    else:
        button_error_and_back_to_initial_state_form(interface)


#CHANGE_PRINT_OPTIONS_IN_ROTA_REPORT_STATE
def display_form_for_rota_report_print_options(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    form_of_print_options = get_saved_print_options_and_create_form(
        interface=interface, report_type=specific_parameters_for_volunteer_report.report_type
        , report_for=str(event)
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


#CHANGE_PRINT_OPTIONS_IN_ROTA_REPORT_STATE
def post_form_for_rota_report_print_options(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()

    previous_form = interface.get_new_display_form_for_parent_of_function(display_form_for_rota_report_print_options)
    if last_button_pressed == BACK_BUTTON_LABEL:
        return previous_form

    elif last_button_pressed == CANCEL_BUTTON_LABEL:
        return initial_state_form

    print_options = get_print_options_from_main_option_form_fields(interface)
    save_print_options(
        report_type=specific_parameters_for_volunteer_report.report_type,
        print_options=print_options, interface=interface
    )
    if last_button_pressed == CREATE_REPORT_BUTTON_LABEL:
        return create_rota_report(interface)

    elif last_button_pressed == SAVE_THESE_OPTIONS_BUTTON_LABEL:
        return previous_form

    else:
        return button_error_and_back_to_initial_state_form(interface)


#CHANGE_GROUP_LAYOUT_IN_ROTA_REPORT_STATE
def display_form_for_group_arrangement_options_rota_report(interface: abstractInterface) -> Form:
    dict_of_df = get_dict_of_df_for_reporting_rota(interface)

    form_for_arrangement_options = form_for_group_arrangement_options(interface=interface,
                                                                      dict_of_df=dict_of_df,
                                                                      specific_parameters_for_type_of_report=specific_parameters_for_volunteer_report)

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



#CHANGE_GROUP_LAYOUT_IN_ROTA_REPORT_STATE
def post_form_for_group_arrangement_options_rota_report(
        interface: abstractInterface,
) -> Union[NewForm, Form, File]:
    last_button_pressed = interface.last_button_pressed()
    previous_form = interface.get_new_display_form_for_parent_of_function(display_form_for_group_arrangement_options_rota_report)

    if last_button_pressed == CREATE_REPORT_BUTTON_LABEL:
        return create_rota_report(interface)

    elif last_button_pressed == BACK_BUTTON_LABEL:
        return previous_form

    elif last_button_pressed == CANCEL_BUTTON_LABEL:
        return initial_state_form
    else:
        ## Changing arrangement
        dict_of_df = get_dict_of_df_for_reporting_rota(interface)
        return post_form_for_group_arrangement_options(interface=interface,
                                                       current_form_function=display_form_for_group_arrangement_options_rota_report,
                                                       dict_of_df=dict_of_df,
                                                       specific_parameters_for_type_of_report=specific_parameters_for_volunteer_report)




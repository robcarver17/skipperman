from typing import Union

from app.backend.reporting.options_and_parameters.print_options import web_pathname_of_report
from app.logic.reporting.shared.arrangement_form import form_for_group_arrangement_options, \
    post_form_for_group_arrangement_options
from app.logic.reporting.shared.create_report import create_generic_report
from app.backend.reporting.event_lists import display_list_of_events_with_buttons_criteria_matched, \
    describe_criteria
from app.logic.reporting.shared.explain_options import get_text_explaining_various_options_for_generic_report
from app.logic.reporting.shared.print_options import (
    save_print_options,
    get_print_options_from_main_option_form_fields,
    get_saved_print_options_and_create_form, get_saved_print_options,
)
from app.logic.reporting.shared.report_generator import ReportGenerator

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


def display_initial_generic_report_form(report_generator: ReportGenerator) -> Form:
    event_criteria= report_generator.event_criteria
    list_of_events = display_list_of_events_with_buttons_criteria_matched(
        **event_criteria
    )
    criteria_description  =describe_criteria(**event_criteria)
    lines_inside_form = ListOfLines(
        [back_button,
         _______________,
         report_generator.name,
         _______________,
         "Select event %s:" %  criteria_description,
         _______________,
         list_of_events]
    )

    return Form(lines_inside_form)

back_button = Button(BACK_BUTTON_LABEL)




def post_form_initial_generic_report(
    interface: abstractInterface,
    report_generator: ReportGenerator
) -> Union[Form, NewForm]:
    last_button = interface.last_button_pressed()
    if last_button == BACK_BUTTON_LABEL:
        return interface.get_new_display_form_for_parent_of_function(report_generator.initial_display_form_function)

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

    return interface.get_new_form_given_function(report_generator.all_options_display_form_function)


def display_form_for_generic_report_all_options(
    interface: abstractInterface,
    report_generator: ReportGenerator

) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    (
        additional_options_as_text,
        print_options_as_text,
        arrangement_and_order_text,
    ) = get_text_explaining_various_options_for_generic_report(interface=interface, report_generator=report_generator)


    link =weblink_for_report(interface=interface, report_generator=report_generator)
    return Form(
        ListOfLines(
            [
                cancel_button,
                back_button,
                _______________,
                bold("%s: Reporting options for %s" % (report_generator.name, str(event))),
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
                link
            ]
        )
    )

def weblink_for_report(interface: abstractInterface, report_generator: ReportGenerator) -> str:
    print_options = get_saved_print_options(report_type=report_generator.specific_parameters_for_type_of_report.report_type, interface=interface)
    if print_options.publish_to_public:
        path = web_pathname_of_report(print_options.filename_with_extension)
        return "Created report can be downloaded and will be found at %s" % path
    else:
        return ""

cancel_button = Button(CANCEL_BUTTON_LABEL)

def post_form_for_generic_report_all_options(
    interface: abstractInterface,
        report_generator: ReportGenerator

) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()
    previous_form = interface.get_new_display_form_for_parent_of_function(report_generator.all_options_display_form_function)

    if last_button_pressed == CREATE_REPORT_BUTTON_LABEL:
        return create_generic_report(interface=interface, report_generator=report_generator)

    elif last_button_pressed == MODIFY_PRINT_OPTIONS_BUTTON_LABEL:
        return print_option_form(interface, report_generator)

    elif last_button_pressed == CHANGE_GROUP_LAYOUT_BUTTON:
        return arrangement_option_form(interface, report_generator)

    elif last_button_pressed == MODIFY_ADDITIONAL_OPTIONS_BUTTON_LABEL:
        return additional_options_form(interface, report_generator)

    elif last_button_pressed == BACK_BUTTON_LABEL:
        # otherwise event/report specific data like filenames is remembered; also group order which could break everything if persisted
        # note if the report type was persistently stored we'd need to keep it here but it is not
        interface.clear_persistent_data_except_specified_fields([])
        return previous_form

    elif last_button_pressed == CANCEL_BUTTON_LABEL:
        return initial_state_form

    else:
        button_error_and_back_to_initial_state_form(interface)


def print_option_form(interface: abstractInterface, report_generator: ReportGenerator):
    return interface.get_new_form_given_function(report_generator.print_options_display_form_function)


def arrangement_option_form(interface: abstractInterface, report_generator: ReportGenerator):
    return interface.get_new_form_given_function(report_generator.arrangement_options_display_form_function)


def additional_options_form(interface: abstractInterface, report_generator: ReportGenerator):
    return interface.get_new_form_given_function(report_generator.additional_options_display_form_function)


def display_form_for_generic_report_additional_options(
    interface: abstractInterface,
        report_generator: ReportGenerator

) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    reporting_options_this_report = report_generator.additional_parameters_form(interface)
    return Form(
        ListOfLines(
            [
                cancel_button,
                back_button,
                _______________,
                "%s: Select additional parameters for %s" % (report_generator.name, str(event)),
                _______________,
                reporting_options_this_report,
                _______________,
                Line([Button(SAVE_THESE_OPTIONS_BUTTON_LABEL), Button(CREATE_REPORT_BUTTON_LABEL)])
            ]
        )
    )


def post_form_for_generic_report_additional_options(
    interface: abstractInterface,
        report_generator: ReportGenerator

) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()
    previous_form = interface.get_new_display_form_for_parent_of_function(report_generator.additional_options_display_form_function)

    if last_button_pressed == BACK_BUTTON_LABEL:
        return previous_form

    elif  last_button_pressed== CREATE_REPORT_BUTTON_LABEL:
        report_generator.get_additional_parameters_from_form_and_save(interface)
        return create_generic_report(interface=interface, report_generator=report_generator)

    elif last_button_pressed == SAVE_THESE_OPTIONS_BUTTON_LABEL:
        report_generator.get_additional_parameters_from_form_and_save(interface)
        return previous_form

    elif last_button_pressed == CANCEL_BUTTON_LABEL:
        return initial_state_form

    else:
        button_error_and_back_to_initial_state_form(interface)

def display_form_for_generic_report_print_options(
    interface: abstractInterface,
    report_generator: ReportGenerator

) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    form_of_print_options = get_saved_print_options_and_create_form(
        interface=interface,
        report_type=report_generator.specific_parameters_for_type_of_report.report_type,
        report_for=str(event)
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


def post_form_for_generic_report_print_options(
    interface: abstractInterface,
    report_generator: ReportGenerator

) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()
    previous_form = interface.get_new_display_form_for_parent_of_function(report_generator.print_options_display_form_function)

    if last_button_pressed == BACK_BUTTON_LABEL:
        return previous_form

    elif last_button_pressed == CANCEL_BUTTON_LABEL:
        return initial_state_form

    #saving
    print_options = get_print_options_from_main_option_form_fields(interface)
    save_print_options(
        report_type=report_generator.specific_parameters_for_type_of_report.report_type, print_options=print_options, interface=interface
    )
    if last_button_pressed == CREATE_REPORT_BUTTON_LABEL:
        return create_generic_report(interface=interface, report_generator=report_generator)

    elif last_button_pressed == SAVE_THESE_OPTIONS_BUTTON_LABEL:
        ## already saved
        return previous_form

    else:
        return button_error_and_back_to_initial_state_form(interface)


def display_form_for_generic_report_arrangement_options(interface: abstractInterface,
                                                        report_generator: ReportGenerator
                                                        ) -> Form:
    dict_of_df = report_generator.get_dict_of_df(interface)

    form_for_arrangement_options = form_for_group_arrangement_options(interface=interface,
                                                                      dict_of_df=dict_of_df,
                                                                      specific_parameters_for_type_of_report=report_generator.specific_parameters_for_type_of_report)

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



def post_form_for_generic_report_arrangement_options(
        interface: abstractInterface,
        report_generator: ReportGenerator

) -> Union[NewForm, Form, File]:
    last_button_pressed = interface.last_button_pressed()
    previous_form = interface.get_new_display_form_for_parent_of_function(report_generator.arrangement_options_display_form_function)

    if last_button_pressed == CREATE_REPORT_BUTTON_LABEL:
        return create_generic_report(interface=interface, report_generator=report_generator)

    elif last_button_pressed == BACK_BUTTON_LABEL:
        return previous_form

    elif last_button_pressed == CANCEL_BUTTON_LABEL:
        return initial_state_form
    else:
        ## Changing arrangement
        dict_of_df = report_generator.get_dict_of_df(interface)
        return post_form_for_group_arrangement_options(interface=interface,
                                                       current_form_function=report_generator.arrangement_options_display_form_function,
                                                       dict_of_df=dict_of_df,
                                                       specific_parameters_for_type_of_report=report_generator.specific_parameters_for_type_of_report)




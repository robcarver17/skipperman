from typing import Union

from app.backend.reporting.arrangement.get_and_update_arrangement_options import (
    reset_arrangement_report_options,
)
from app.backend.reporting.event_lists import (
    display_list_of_events_with_buttons_criteria_matched,
    describe_criteria,
)
from app.frontend.reporting.shared.arrangement_form import (
    form_for_group_arrangement_options,
    post_form_for_group_arrangement_options,
)
from app.frontend.reporting.shared.create_report import (
    create_generic_report,
    qr_code_for_report,
)
from app.frontend.reporting.shared.explain_options import (
    get_text_explaining_various_options_for_generic_report,
)
from app.frontend.reporting.shared.print_options import (
    get_saved_print_options_and_create_form,
    reset_print_report_options,
    save_print_options_from_form,
    qr_button,
)
from app.backend.reporting.report_generator import (
    ReportGeneratorWithoutSpecificParameters,
)
from app.frontend.reporting.shared.reporting_options import (
    reset_all_report_options,
    reset_specific_report_options,
)
from app.frontend.shared.buttons import (
    is_button_event_selection,
    event_from_button_pressed,
)

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects.abstract_objects.abstract_text import bold, Heading
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    main_menu_button,
    back_menu_button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.form_handler import (
    button_error_and_back_to_initial_state_form,
)
from app.frontend.shared.events_state import (
    get_event_from_state,
    update_state_for_specific_event,
)


def display_initial_generic_report_form(
    interface: abstractInterface,
    report_generator: ReportGeneratorWithoutSpecificParameters,
) -> Form:
    report_generator_with_specific_parameters = (
        report_generator.add_specific_parameters_for_type_of_report(
            interface.object_store,

        )
    )

    event_criteria = report_generator_with_specific_parameters.event_criteria
    list_of_events = display_list_of_events_with_buttons_criteria_matched(
        object_store=interface.object_store, event_criteria=event_criteria
    )
    criteria_description = describe_criteria(**event_criteria)
    help_button = HelpButton(report_generator_with_specific_parameters.help_page)
    nav_bar = ButtonBar([main_menu_button, back_menu_button, help_button])

    heading = Heading(
        "Select event for %s %s:"
        % (report_generator_with_specific_parameters.report_type, criteria_description),
        centred=True,
        size=4,
    )
    lines_inside_form = ListOfLines(
        [nav_bar, _______________, heading, _______________, list_of_events]
    )

    return Form(lines_inside_form)


def post_form_initial_generic_report(
    interface: abstractInterface,
    report_generator: ReportGeneratorWithoutSpecificParameters,
) -> Union[Form, NewForm]:
    last_button = interface.last_button_pressed()
    if back_menu_button.pressed(last_button):
        return interface.get_new_display_form_for_parent_of_function(
            report_generator.initial_display_form_function
        )
    elif is_button_event_selection(last_button):
        return action_when_event_button_clicked(
            interface=interface, report_generator=report_generator
        )
    else:
        return button_error_and_back_to_initial_state_form(interface)


def action_when_event_button_clicked(
    interface: abstractInterface,
    report_generator: ReportGeneratorWithoutSpecificParameters,
):
    ## so whilst we are in this stage, we know which event we are talking about
    event = event_from_button_pressed(
        value_of_button_pressed=interface.last_button_pressed(),
        object_store=interface.object_store,
    )
    update_state_for_specific_event(interface=interface, event=event)

    return interface.get_new_form_given_function(
        report_generator.all_options_display_form_function
    )


def display_form_for_generic_report_all_options(
    interface: abstractInterface,
    report_generator: ReportGeneratorWithoutSpecificParameters,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    report_generator_with_specific_parameters = (
        report_generator.add_specific_parameters_for_type_of_report(
            interface.object_store,
            event=event
        )
    )

    (
        additional_options_as_text,
        print_options_as_text,
        arrangement_and_order_text,
    ) = get_text_explaining_various_options_for_generic_report(
        interface=interface, report_generator=report_generator_with_specific_parameters
    )
    help_button = HelpButton(report_generator_with_specific_parameters.help_page)
    navbar = ButtonBar(
        [
            main_menu_button,
            back_menu_button,
            create_report_button,
            reset_all_options_button,
            help_button,
        ]
    )

    return Form(
        ListOfLines(
            [
                navbar,
                _______________,
                Heading(
                    "%s: Reporting options for %s"
                    % (
                        report_generator_with_specific_parameters.report_type,
                        str(event),
                    ),
                    size=4,
                    centred=True,
                ),
                _______________,
                ButtonBar([modify_additional_options_button]),
                bold("Specific options for this report"),
                additional_options_as_text,
                _______________,
                ButtonBar([modify_print_options_button]),
                print_options_as_text,
                _______________,
                ButtonBar([modify_group_layout_button]),
                arrangement_and_order_text,
                _______________,
            ]
        )
    )


def post_form_for_generic_report_all_options(
    interface: abstractInterface,
    report_generator: ReportGeneratorWithoutSpecificParameters,
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()
    previous_form = interface.get_new_display_form_for_parent_of_function(
        report_generator.all_options_display_form_function
    )
    report_generator_with_specific_parameters = (
        report_generator.add_specific_parameters_for_type_of_report(
            interface.object_store,
            event=get_event_from_state(interface)
        )
    )

    if create_report_button.pressed(last_button_pressed):
        return create_generic_report(
            interface=interface,
            report_generator=report_generator_with_specific_parameters,
        )
    elif qr_button.pressed(last_button_pressed):
        return qr_code_for_report(interface, report_generator_with_specific_parameters)

    elif modify_print_options_button.pressed(last_button_pressed):
        return interface.get_new_form_given_function(report_generator.print_options_display_form_function)

    elif modify_group_layout_button.pressed(last_button_pressed):
        return interface.get_new_form_given_function(report_generator.arrangement_options_display_form_function)

    elif modify_additional_options_button.pressed(last_button_pressed):
        return interface.get_new_form_given_function(report_generator.additional_options_display_form_function)

    elif reset_all_options_button.pressed(last_button_pressed):
        reset_all_report_options(interface, report_generator_with_specific_parameters)
        interface.flush_and_clear()
        return interface.get_new_form_given_function(report_generator.all_options_display_form_function)

    elif back_menu_button.pressed(last_button_pressed):
        # otherwise event/report specific data like filenames is remembered; also group order which could break everything if persisted
        # note if the report type was persistently stored we'd need to keep it here but it is not
        interface.clear_persistent_data_for_action()
        return previous_form

    else:
        button_error_and_back_to_initial_state_form(interface)

def display_form_for_generic_report_additional_options(
    interface: abstractInterface,
    report_generator: ReportGeneratorWithoutSpecificParameters,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    report_generator_with_specific_parameters = (
        report_generator.add_specific_parameters_for_type_of_report(
            interface.object_store,
            event=event
        )
    )
    help_button = HelpButton(report_generator_with_specific_parameters.help_page)

    reporting_options_this_report = (
        report_generator_with_specific_parameters.additional_parameters_form(interface)
    )
    return Form(
        ListOfLines(
            [
                ButtonBar(
                    [
                        back_menu_button,
                        create_report_button,
                        save_button,
                        reset_specific_options_button,
                        help_button,
                    ]
                ),
                _______________,
                Heading(
                    "%s: Select report specific parameters for %s"
                    % (
                        report_generator_with_specific_parameters.report_type,
                        str(event),
                    ),
                    centred=False,
                    size=6,
                ),
                _______________,
                reporting_options_this_report,
                _______________,
            ]
        )
    )


def post_form_for_generic_report_additional_options(
    interface: abstractInterface,
    report_generator: ReportGeneratorWithoutSpecificParameters,
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()
    previous_form = interface.get_new_display_form_for_parent_of_function(
        report_generator.additional_options_display_form_function
    )
    report_generator_with_specific_parameters = (
        report_generator.add_specific_parameters_for_type_of_report(
            interface.object_store,
            event=get_event_from_state(interface)
        )
    )

    if back_menu_button.pressed(last_button_pressed):
        return previous_form


    if reset_specific_options_button.pressed(last_button_pressed):
        
        reset_specific_report_options(
            interface, report_generator_with_specific_parameters
        )
        interface.flush_and_clear()
        return interface.get_new_form_given_function(report_generator.additional_options_display_form_function)

    elif create_report_button.pressed(last_button_pressed):
        report_generator.get_additional_parameters_from_form_and_save(
            interface=interface,
            report_generator=report_generator_with_specific_parameters,
        )
        interface.flush_and_clear()
        return create_generic_report(
            interface=interface,
            report_generator=report_generator_with_specific_parameters,
        )
    elif save_button.pressed(last_button_pressed):
        
        report_generator.get_additional_parameters_from_form_and_save(
            interface=interface,
            report_generator=report_generator_with_specific_parameters,
        )
        interface.flush_and_clear()
        return previous_form
    else:
        button_error_and_back_to_initial_state_form(interface)


def display_form_for_generic_report_print_options(
    interface: abstractInterface,
    report_generator: ReportGeneratorWithoutSpecificParameters,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    report_generator_with_specific_parameters = (
        report_generator.add_specific_parameters_for_type_of_report(
            interface.object_store,
            event=event
        )
    )
    specific_parameters_for_type_of_report = (
        report_generator_with_specific_parameters.specific_parameters_for_type_of_report
    )

    form_of_print_options = get_saved_print_options_and_create_form(
        interface=interface,
        report_type=specific_parameters_for_type_of_report.report_type,
        report_for=str(event),
    )
    help_button = HelpButton("general_report_config_and_printing_help#print-options")

    return Form(
        ListOfLines(
            [
                ButtonBar(
                    [
                        back_menu_button,
                        save_button,
                        create_report_button,
                        reset_print_options_button,
                        help_button,
                    ]
                ),
                _______________,
            ]
        )
        + form_of_print_options
        + ListOfLines(
            [
                _______________,
            ]
        )
    )


def post_form_for_generic_report_print_options(
    interface: abstractInterface,
    report_generator: ReportGeneratorWithoutSpecificParameters,
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()
    previous_form = interface.get_new_display_form_for_parent_of_function(
        report_generator.print_options_display_form_function
    )
    report_generator_with_specific_parameters = (
        report_generator.add_specific_parameters_for_type_of_report(
            object_store=interface.object_store,
            event=get_event_from_state(interface)
        )
    )

    if back_menu_button.pressed(last_button_pressed):
        return previous_form

    elif reset_print_options_button.pressed(last_button_pressed):
        
        reset_print_report_options(
            interface=interface,
            report_generator=report_generator_with_specific_parameters,
        )
        interface.flush_and_clear()
        return interface.get_new_form_given_function(report_generator.print_options_display_form_function)

    elif create_report_button.pressed(last_button_pressed):
        
        save_print_options_from_form(
            interface=interface,
            report_generator=report_generator_with_specific_parameters,
        )
        interface.flush_and_clear()
        return create_generic_report(
            interface=interface,
            report_generator=report_generator_with_specific_parameters,
        )

    elif save_button.pressed(last_button_pressed):
        
        save_print_options_from_form(
            interface=interface,
            report_generator=report_generator_with_specific_parameters,
        )
        interface.flush_and_clear()
        return previous_form

    else:
        return button_error_and_back_to_initial_state_form(interface)


def display_form_for_generic_report_arrangement_options(
    interface: abstractInterface,
    report_generator: ReportGeneratorWithoutSpecificParameters,
) -> Form:
    dict_of_df = report_generator.get_dict_of_df(interface)
    report_generator_with_specific_parameters = (
        report_generator.add_specific_parameters_for_type_of_report(
            interface.object_store,
            event=get_event_from_state(interface)
        )
    )
    specific_parameters_for_type_of_report = (
        report_generator_with_specific_parameters.specific_parameters_for_type_of_report
    )

    form_for_arrangement_options = form_for_group_arrangement_options(
        interface=interface,
        dict_of_df=dict_of_df,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
    )
    event = get_event_from_state(interface)
    help_button = HelpButton(
        "general_report_config_and_printing_help#arrangement-options"
    )

    return Form(
        ListOfLines(
            [
                ButtonBar(
                    [
                        back_menu_button,
                        create_report_button,
                        reset_layout_options_button,
                        help_button,
                    ]
                ),
                Heading(
                    "%s: Arrange layout for %s"
                    % (
                        report_generator_with_specific_parameters.report_type,
                        str(event),
                    ),
                    centred=False,
                    size=6,
                ),
                form_for_arrangement_options,
                _______________,
            ]
        )
    )


def post_form_for_generic_report_arrangement_options(
    interface: abstractInterface,
    report_generator: ReportGeneratorWithoutSpecificParameters,
) -> Union[NewForm, Form, File]:
    last_button_pressed = interface.last_button_pressed()
    previous_form = interface.get_new_display_form_for_parent_of_function(
        report_generator.arrangement_options_display_form_function
    )

    report_generator_with_specific_parameters = (
        report_generator.add_specific_parameters_for_type_of_report(
            interface.object_store,
            event=get_event_from_state(interface)
        )
    )
    specific_parameters_for_type_of_report = (
        report_generator_with_specific_parameters.specific_parameters_for_type_of_report
    )

    if back_menu_button.pressed(last_button_pressed):
        return previous_form

    elif create_report_button.pressed(last_button_pressed):
        ## No need to save first as only buttons in form

        return create_generic_report(
            interface=interface,
            report_generator=report_generator_with_specific_parameters,
        )

    elif reset_layout_options_button.pressed(last_button_pressed):
        
        reset_arrangement_report_options(
            object_store=interface.object_store,
            report_generator=report_generator_with_specific_parameters,
        )
        interface.flush_and_clear()
        return interface.get_new_form_given_function(report_generator.arrangement_options_display_form_function)

    else:
        ## Changing arrangement
        dict_of_df = report_generator.get_dict_of_df(interface)

        return post_form_for_group_arrangement_options(
            interface=interface,
            current_form_function=report_generator.arrangement_options_display_form_function,
            dict_of_df=dict_of_df,
            specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
        )


SAVE_THESE_OPTIONS_BUTTON_LABEL = "Save these print options"
CREATE_REPORT_BUTTON_LABEL = "Create report with these options"

MODIFY_PRINT_OPTIONS_BUTTON_LABEL = "Modify printing options"
CHANGE_GROUP_LAYOUT_BUTTON = "Modify group layout"
MODIFY_ADDITIONAL_OPTIONS_BUTTON_LABEL = "Modify report specific options"
RESET_ALL_PRINT_OPTIONS = "Reset all print options"
RESET_PRINTING_OPTIONS = "Reset printing options"
RESET_SPECIFIC_OPTIONS = "Reset report specific options"
RESET_LAYOUT_OPTIONS = "Reset arrangement options"

save_button = Button(SAVE_THESE_OPTIONS_BUTTON_LABEL, nav_button=True)

modify_additional_options_button = Button(
    MODIFY_ADDITIONAL_OPTIONS_BUTTON_LABEL, nav_button=True
)
modify_print_options_button = Button(MODIFY_PRINT_OPTIONS_BUTTON_LABEL, nav_button=True)
modify_group_layout_button = Button(CHANGE_GROUP_LAYOUT_BUTTON, nav_button=True)
create_report_button = Button(CREATE_REPORT_BUTTON_LABEL, nav_button=True)
reset_print_options_button = Button(RESET_PRINTING_OPTIONS, nav_button=True)
reset_all_options_button = Button(RESET_ALL_PRINT_OPTIONS, nav_button=True)
reset_specific_options_button = Button(RESET_SPECIFIC_OPTIONS, nav_button=True)
reset_layout_options_button = Button(RESET_LAYOUT_OPTIONS, nav_button=True)

from typing import Union

import pandas as pd

from app.logic.reporting.options.arrangements import get_stored_arrangement, save_arrangement, \
    create_arrangement_from_order_and_algo_and_save, augment_order_of_groups_with_sizes
from app.logic.reporting.options.group_order import get_group_order_from_stored_or_df, get_stored_group_order, \
    save_group_order_to_storage
from app.logic.reporting.options.print_options import get_saved_print_options, save_print_options, \
    report_print_options_as_list_of_lines, get_print_options_from_main_option_form_fields, \
    report_print_options_as_form_contents
from app.reporting.process_stages.create_column_pdf_report_from_df import create_column_pdf_report_from_df_and_return_filename


from app.objects.field_list import CADET_NAME, GROUP_STR_NAME
from app.data_access.configuration.configuration import ALL_GROUPS

from app.reporting.options_and_parameters.report_type_specific_parameters import SpecificParametersForTypeOfReport

from app.logic.forms_and_interfaces.abstract_form import Form, NewForm, ListOfLines, _______________, back_button, yes_no_radio, cancel_button, Button, File, \
    bold, Line, BACK_BUTTON_LABEL
from app.logic.forms_and_interfaces.reorder_form import reorder_table, reorderFormInterface
from app.logic.forms_and_interfaces.reorder_matrix import reorder_matrix, reorderMatrixInterface
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import initial_state_form
from app.logic.events.utilities import get_event_from_state, confirm_event_exists, update_state_for_specific_event
from app.logic.allocation.allocations_data import get_df_for_reporting_allocations_with_flags

from app.logic.reporting.constants import *
from app.logic.events.view_events import display_list_of_events_with_buttons

from app.objects.reporting_options import describe_arrangement
from app.reporting.arrangement.arrangement_methods import ARRANGE_PASSED_LIST, POSSIBLE_ARRANGEMENTS_NOT_PASSING
from app.reporting.arrangement.arrange_options import describe_arrangement

REPORT_NAME = "Allocation report"

def display_form_report_group_allocation(
interface: abstractInterface
) -> Form:
    list_of_events = display_list_of_events_with_buttons()
    lines_inside_form = ListOfLines([
        back_button,
        _______________,
        "Select event:",
        _______________,
        list_of_events
        ]
    )

    return Form(lines_inside_form)



def post_form_report_group_allocation(interface: abstractInterface) -> Union[Form, NewForm]:
    event_name_selected = interface.last_button_pressed()
    if event_name_selected == BACK_BUTTON_LABEL:
        return initial_state_form
    try:
        confirm_event_exists(event_name_selected)
    except:
        interface.log_error("Event %s no longer in list- someone else has deleted or file corruption?"
            % event_name_selected)
        return initial_state_form

    ## so whilst we are in this stage, we know which event we are talking about
    update_state_for_specific_event(
        interface=interface, event_selected=event_name_selected)

    return NewForm(REPORT_ADDITIONAL_OPTIONS_FOR_ALLOCATION_REPORT)

def display_form_for_report_group_allocation_options(interface:abstractInterface)-> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    reporting_options_this_report = reporting_options_form_for_group_allocation()
    return Form(ListOfLines([
        cancel_button,
        back_button,
        _______________,
        "Allocation report: Select reporting options for %s" % str(event),
        _______________,
        reporting_options_this_report,
        _______________,
        Button(USE_THESE_OPTIONS_BUTTON_LABEL)
    ]))

def reporting_options_form_for_group_allocation() -> ListOfLines:
    my_options = ListOfLines([
        yes_no_radio(input_label="Show full names? (no to include first initial and surname only)", input_name=SHOW_FULL_NAMES, default_is_yes=False),
        yes_no_radio(input_label="Include unallocated cadets?", input_name=INCLUDE_UNALLOCATED_CADETS, default_is_yes=False),
        _______________
        ]
    )
    return my_options

def post_form_for_report_group_allocation_options(interface:abstractInterface)-> Union[Form, NewForm]:
    if interface.last_button_pressed()==BACK_BUTTON_LABEL:
        return NewForm(GROUP_ALLOCATION_REPORT_STAGE)
    elif interface.last_button_pressed()==USE_THESE_OPTIONS_BUTTON_LABEL:
        display_full_names = interface.true_if_radio_was_yes(SHOW_FULL_NAMES)
        include_unallocated_cadets = interface.true_if_radio_was_yes(INCLUDE_UNALLOCATED_CADETS)
        interface.set_persistent_value(SHOW_FULL_NAMES, display_full_names)
        interface.set_persistent_value(INCLUDE_UNALLOCATED_CADETS, include_unallocated_cadets)

        return NewForm(GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE)
    else:
        interface.log_error("Button %s not recognised" % interface.last_button_pressed())


default_markuplist_from_df_options_for_group_allocation = SpecificParametersForTypeOfReport(
    entry_columns=[CADET_NAME],
    group_by_column=GROUP_STR_NAME,
    passed_group_order=ALL_GROUPS,
)

def display_form_for_report_group_allocation_generic_options(interface:abstractInterface) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    print_options = get_saved_print_options(REPORT_NAME, interface=interface)
    print_options_as_text = report_print_options_as_list_of_lines(print_options)

    df = get_df_for_reporting_allocations(interface)
    order_of_groups = get_group_order_from_stored_or_df(interface=interface,
                                                        report_type_specific_parameters=default_markuplist_from_df_options_for_group_allocation,
                                                        df=df)
    order_of_groups_as_text = ", ".join(order_of_groups)

    arrangement = get_stored_arrangement(interface)
    arrangement_text = describe_arrangement(arrangement)

    return Form(ListOfLines([
        cancel_button,
        back_button,
        _______________,
        bold("Allocation report: Select more reporting options for %s" % str(event)),
        _______________,
        bold("Print Options:"),
        print_options_as_text,
        Button(MODIFY_PRINT_OPTIONS_BUTTON_LABEL),
        _______________,
        bold("Order and arrangement of groups:"),
        "Order: %s" % order_of_groups_as_text,
        "Arrangement: %s" % arrangement_text,
        Button(CHANGE_GROUP_LAYOUT_BUTTON),
        _______________,
        Button(CREATE_REPORT_BUTTON_LABEL)
    ]))


def post_form_for_report_group_allocation_generic_options(interface:abstractInterface) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed==CREATE_REPORT_BUTTON_LABEL:
        return create_report(interface)

    elif last_button_pressed==MODIFY_PRINT_OPTIONS_BUTTON_LABEL:
        return NewForm(CHANGE_PRINT_OPTIONS_IN_GROUP_ALLOCATION_STATE)

    elif last_button_pressed==CHANGE_GROUP_LAYOUT_BUTTON:
        return NewForm(CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE)

    elif last_button_pressed==BACK_BUTTON_LABEL:
        return NewForm(REPORT_ADDITIONAL_OPTIONS_FOR_ALLOCATION_REPORT)

    else:
        interface.log_error("Button %s not recognised" % last_button_pressed)
        return initial_state_form

def display_form_for_report_group_allocation_print_options(interface: abstractInterface) -> Union[
    Form, NewForm]:
    event = get_event_from_state(interface)
    print_options = get_saved_print_options(REPORT_NAME, interface=interface)
    report_options_within_form = report_print_options_as_form_contents(print_options)

    return Form(ListOfLines([
        cancel_button,
        _______________,
        "%s: Select print options for %s" % (REPORT_NAME, str(event)),
        _______________,
        report_options_within_form,
        _______________,
        Line([back_button, Button(SAVE_THESE_OPTIONS_BUTTON_LABEL), Button(CREATE_REPORT_BUTTON_LABEL)])
    ]))

def post_form_for_report_group_allocation_print_options(interface: abstractInterface) -> Union[
    Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()

    if last_button_pressed==BACK_BUTTON_LABEL:
        return NewForm(GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE)

    if last_button_pressed in [CREATE_REPORT_BUTTON_LABEL, SAVE_THESE_OPTIONS_BUTTON_LABEL]:
        print_options =get_print_options_from_main_option_form_fields(interface)
        save_print_options(REPORT_NAME, print_options=print_options, interface=interface)

    if last_button_pressed==CREATE_REPORT_BUTTON_LABEL:
        return create_report(interface)
    elif last_button_pressed==SAVE_THESE_OPTIONS_BUTTON_LABEL:
        print("Saving print options")
        return NewForm(GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE)
    else:
        interface.log_error("Button %s not recognised" % last_button_pressed)
        return initial_state_form



def display_form_for_group_arrangement_options(interface: abstractInterface) -> Form:
    arrangement_options = get_stored_arrangement(interface)
    print_options = get_saved_print_options(interface=interface, report_type=REPORT_NAME)
    df = get_df_for_reporting_allocations(interface)
    order_of_groups = get_group_order_from_stored_or_df(interface=interface,
                                                        report_type_specific_parameters=default_markuplist_from_df_options_for_group_allocation,
                                                        df=df)

    if arrangement_options.no_arrangement_of_columns_provided:
        print("No arrangement provided creating one")
        ## create an arrangement using the current algo
        arrangement_of_columns = create_arrangement_from_order_and_algo_and_save(df=df, current_order=order_of_groups, interface=interface,
                                                                              marked_up_list_from_df_parameters=default_markuplist_from_df_options_for_group_allocation,
                                                                              arrangement_options=arrangement_options, print_options=print_options)
    else:
        arrangement_of_columns = arrangement_options.arrangement_of_columns

    print("arrangement %s" % str(arrangement_of_columns))
    arrangement_of_rows = arrangement_of_columns.transpose_to_rows()
    print("arrangement %s" % str(arrangement_of_rows))

    reorder_list_form = reorder_table("Change order of groups then choose auto-layout", include_finished_button=False,
                                      starting_list=order_of_groups)

    auto_layout_buttons = Line(["Click to auto-layout based on group order above"]+[
            Button(arrangement_description) for arrangement_description in dict_of_arrangements_that_reorder.keys()
    ])

    order_of_groups_with_numbers = augment_order_of_groups_with_sizes(df=df,
                                                                      order_of_groups=order_of_groups,
                                                                      marked_up_list_from_df_parameters=default_markuplist_from_df_options_for_group_allocation,
                                                                      print_options=print_options)
    reorder_matrix_form = reorder_matrix(heading="Manually modify layout (number in bracket shows size of group)", current_list_of_entries=order_of_groups_with_numbers,
                                         arrangement_of_rows=arrangement_of_rows, include_finished_button=False)

    return Form(
        ListOfLines(
            [
                cancel_button,
                reorder_list_form,
                _______________,
                auto_layout_buttons,
                _______________,
                reorder_matrix_form,
                _______________,
                Line([back_button,  Button(CREATE_REPORT_BUTTON_LABEL)])
            ]
        )
    )




dict_of_arrangements_that_reorder = dict(
    [
        (describe_arrangement(arrangement), arrangement)
        for arrangement in POSSIBLE_ARRANGEMENTS_NOT_PASSING
    ]
)





def post_form_for_group_arrangement_options(interface: abstractInterface) -> Union[NewForm, Form, File]:
    last_button_pressed = interface.last_button_pressed()
    print("Button %s" % last_button_pressed)
    arrangement_options = get_stored_arrangement(interface)

    if last_button_pressed == CREATE_REPORT_BUTTON_LABEL:
        return create_report(interface)
    elif last_button_pressed==BACK_BUTTON_LABEL:
        return NewForm(GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE)

    if last_button_pressed in list(dict_of_arrangements_that_reorder.keys()):
        print("Changing arrangement to %s" % last_button_pressed)
        arrangement_method = dict_of_arrangements_that_reorder[last_button_pressed]
        arrangement_options.arrangement = arrangement_method
        arrangement_options.delete_arrangement_of_columns()
        print("New arrangement options %s" % str(arrangement_options))
        save_arrangement(arrangement_options=arrangement_options, interface=interface)

        return NewForm(CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE)

    ## Change in order of list
    order_of_groups = get_stored_group_order(interface)
    reorder_form_interface = reorderFormInterface(interface, current_order=order_of_groups)

    try:
        indices_to_swap = reorder_form_interface.indices_to_swap()
        ## Need to modify the indices in the matrix layout or that will change when should not
        arrangement_options = get_stored_arrangement(interface)
        arrangement_options.arrangement_of_columns.swap_indices(indices_to_swap)
        save_arrangement(arrangement_options=arrangement_options, interface=interface)

        new_order = reorder_form_interface.new_order_of_list()
        save_group_order_to_storage(interface=interface, groups_in_order=new_order)


        return NewForm(CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE)
    except:
        pass

    ## Matrix update

    print_options = get_saved_print_options(interface=interface, report_type=REPORT_NAME)
    df = get_df_for_reporting_allocations(interface)

    order_of_groups_with_numbers = augment_order_of_groups_with_sizes(df=df,
                                                                      order_of_groups=order_of_groups,
                                                                      marked_up_list_from_df_parameters=default_markuplist_from_df_options_for_group_allocation,
                                                                      print_options=print_options)

    reorder_matrix_interface = reorderMatrixInterface(interface=interface, current_arrangement_of_columns=arrangement_options.arrangement_of_columns,
                                                      current_list_of_entries=order_of_groups_with_numbers)

    try:
        arrangement_of_columns = reorder_matrix_interface.new_arrangement()
    except:
        raise Exception("Button not working")

    arrangement_options.arrangement_of_columns = arrangement_of_columns
    arrangement_options.arrangement = ARRANGE_PASSED_LIST
    save_arrangement(arrangement_options=arrangement_options, interface=interface)

    return NewForm(CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE)

def get_df_for_reporting_allocations(interface:abstractInterface) -> pd.DataFrame:
    event = get_event_from_state(interface)
    display_full_names = interface.get_persistent_value(SHOW_FULL_NAMES)
    include_unallocated_cadets = interface.get_persistent_value(INCLUDE_UNALLOCATED_CADETS)
    df = get_df_for_reporting_allocations_with_flags(event = event, include_unallocated_cadets=include_unallocated_cadets, display_full_names=display_full_names)

    return df


def create_report(interface: abstractInterface) -> File:
    df = get_df_for_reporting_allocations(interface)
    report_options = None  ## get from state and saved
    filename = create_column_pdf_report_from_df_and_return_filename(report_options=report_options, df=df)

    return File(filename)
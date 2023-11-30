from typing import Union

import pandas as pd

from app.logic.reporting.reporting_options import get_saved_print_options ,report_print_options_as_form_contents, get_print_options_from_main_option_form_fields, save_print_options, report_print_options_as_list_of_lines, get_list_of_natural_groups, save_list_of_natural_groups, get_stored_natural_groups, get_stored_arrangement, save_arrangement
from app.logic.reporting.backend.create_column_pdf_report_from_df import create_column_pdf_report_from_df_and_return_filename


from app.objects.field_list import CADET_NAME, GROUP_STR_NAME
from app.data_access.configuration.configuration import ALL_GROUPS

from app.objects.reporting_options import MarkedUpListFromDfParameters, describe_arrangement

from app.logic.forms_and_interfaces.abstract_form import Form, NewForm, ListOfLines, _______________, back_button, yes_no_radio, cancel_button, Button, File, \
    bold
from app.logic.forms_and_interfaces.reorder_form import reorder_form, reorderFormInterface
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import initial_state_form
from app.logic.events.utilities import get_event_from_state, confirm_event_exists, update_state_for_specific_event
from app.logic.allocation.allocations_data import get_df_for_reporting_allocations_with_flags

from app.logic.reporting.constants import *
from app.logic.events.view_events import display_list_of_events_with_buttons

from app.objects.reporting_options import describe_arrangement, POSSIBLE_ARRANGEMENTS

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

    try:
        confirm_event_exists(event_name_selected)
    except:
        interface.log_error("Event %s no longer in list- someone else has deleted or file corruption?"
            % event_name_selected)
        return initial_state_form

    ## so whilst we are in this stage, we know which event we are talking about
    update_state_for_specific_event(
        interface=interface, event_selected=event_name_selected)

    return NewForm(REPORT_OPTIONS_IN_GROUP_ALLOCATION_STATE)

def display_form_for_report_group_allocation_options(interface:abstractInterface)-> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    reporting_options_this_report = reporting_options_form_for_group_allocation()
    return Form(ListOfLines([
        cancel_button,
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
    display_full_names = interface.true_if_radio_was_yes(SHOW_FULL_NAMES)
    include_unallocated_cadets = interface.true_if_radio_was_yes(INCLUDE_UNALLOCATED_CADETS)
    interface.set_persistent_value(SHOW_FULL_NAMES, display_full_names)
    interface.set_persistent_value(INCLUDE_UNALLOCATED_CADETS, include_unallocated_cadets)

    return NewForm(GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE)



default_markuplist_from_df_options_for_group_allocation = MarkedUpListFromDfParameters(
    entry_columns=[CADET_NAME],
    group_by_column=GROUP_STR_NAME,
    passed_group_order=ALL_GROUPS,
)

def display_form_for_report_group_allocation_generic_options(interface:abstractInterface) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    print_options = get_saved_print_options(REPORT_NAME, interface=interface)
    print_options_as_text = report_print_options_as_list_of_lines(print_options)

    df = get_df_for_reporting_allocations(interface)
    order_of_groups = get_list_of_natural_groups(df=df, marked_up_list_from_df_parameters=default_markuplist_from_df_options_for_group_allocation, interface=interface)
    order_of_groups_as_text = ", ".join(order_of_groups)

    arrangement = get_stored_arrangement(interface)
    arrangement_text = describe_arrangement(arrangement)

    return Form(ListOfLines([
        cancel_button,
        _______________,
        bold("Allocation report: Select more reporting options for %s" % str(event)),
        _______________,
        bold("Print Options:"),
        print_options_as_text,
        Button(MODIFY_PRINT_OPTIONS_BUTTON_LABEL),
        _______________,
        bold("Order of groups:"),
        order_of_groups_as_text,
        Button(CHANGE_ORDER_OF_GROUPS_BUTTON_LABEL),
        _______________,
        bold("Arrangement of groups:"),
        arrangement_text,
        Button(CHANGE_GROUP_LAYOUT_BUTTON),
        _______________,
        Button(USE_THESE_OPTIONS_BUTTON_LABEL)
    ]))


def post_form_for_report_group_allocation_generic_options(interface:abstractInterface) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed==USE_THESE_OPTIONS_BUTTON_LABEL:
        df = get_df_for_reporting_allocations(interface)
        report_options = None ## get from state and saved
        filename = create_column_pdf_report_from_df_and_return_filename(report_options=report_options, df=df)

        return File(filename)

    elif last_button_pressed==MODIFY_PRINT_OPTIONS_BUTTON_LABEL:
        return NewForm(CHANGE_PRINT_OPTIONS_IN_GROUP_ALLOCATION_STATE)

    elif last_button_pressed==CHANGE_GROUP_LAYOUT_BUTTON:
        return NewForm(CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE)

    elif last_button_pressed==CHANGE_ORDER_OF_GROUPS_BUTTON_LABEL:
        return NewForm(CHANGE_GROUP_ORDER_IN_GROUP_ALLOCATION_STATE)

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
        Button(USE_THESE_OPTIONS_BUTTON_LABEL)
    ]))

def post_form_for_report_group_allocation_print_options(interface: abstractInterface) -> Union[
    Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed == USE_THESE_OPTIONS_BUTTON_LABEL:
        print_options =get_print_options_from_main_option_form_fields(interface)
        save_print_options(REPORT_NAME, print_options=print_options, interface=interface)
        return NewForm(GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE) ## back to other options
    else:
        interface.log_error("Button %s not recognised" % last_button_pressed)
        return initial_state_form


def display_form_for_group_order_allocation_options(interface: abstractInterface) -> [Form, reorder_form]:
    order_of_groups = get_stored_natural_groups(interface) ## should be stored when we come to submenu

    return reorder_form(heading="Choose order for group allocation", starting_list=order_of_groups, finished_button_label = USE_THESE_OPTIONS_BUTTON_LABEL)

def post_form_for_group_order_allocation_options(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Need to react to order changes, and know current order
    order_of_groups = get_stored_natural_groups(interface)  ## should be stored when we come to submenu
    reorder_form_interface = reorderFormInterface(interface=interface, current_order=order_of_groups)

    if reorder_form_interface.finished():
        ## don't need to store results as would have been stored on last presss
        return  NewForm(GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE)
    else:
        ## save and store results using reorder form
        new_order = reorder_form_interface.new_order_of_list()
        save_list_of_natural_groups(groups_in_order=new_order, interface=interface)
        ## iterate again
        return NewForm(CHANGE_GROUP_ORDER_IN_GROUP_ALLOCATION_STATE)

def display_form_for_group_arrangement_options(interface: abstractInterface) -> Form:
    arrangement = get_stored_arrangement(interface)
    print(arrangement)
    if arrangement.no_list_provided:
        return display_form_for_group_arrangement_options_if_order_not_required(interface)
    else:
        return display_form_for_group_arrangement_options_if_order_required(interface)

dict_of_arrangements = dict(
    [
        (describe_arrangement(arrangement), arrangement)
        for arrangement in POSSIBLE_ARRANGEMENTS
    ]
)

def display_form_for_group_arrangement_options_if_order_not_required(interface: abstractInterface) -> Form:
    ## GET CURRENT ORDER OR DEFAULT
    current_arrangement_options = get_stored_arrangement(interface)
    arrangement_text = describe_arrangement(current_arrangement_options)
    return Form(
            [ "Current arrangement: %s" % arrangement_text, Button(USE_THIS_OPTIONS_BUTTON_LABEL), _______________,]+        ListOfLines([
            Button(arrangement_description) for arrangement_description in dict_of_arrangements.keys() if not dict_of_arrangements[arrangement_description] == current_arrangement_options.arrangement
    ])
    )



def display_form_for_group_arrangement_options_if_order_required(interface: abstractInterface) -> Form:
    raise NotImplemented("shouldn't be here!")


def post_form_for_group_arrangement_options(interface: abstractInterface) -> Union[NewForm, Form]:
    ## Need to react to order changes, and know current order
    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed == USE_THIS_OPTIONS_BUTTON_LABEL:
        return NewForm(GENERIC_OPTIONS_IN_GROUP_ALLOCATION_STATE)
    elif last_button_pressed in list(dict_of_arrangements.keys()):
        current_arrangement_options = get_stored_arrangement(interface)
        arrangement = dict_of_arrangements[last_button_pressed]
        current_arrangement_options.arrangement = arrangement
        save_arrangement(arrangement_options=current_arrangement_options, interface=interface)

        return NewForm(CHANGE_GROUP_LAYOUT_IN_GROUP_ALLOCATION_STATE)
    else:
        interface.log_error("Button %s not recognised!" % last_button_pressed)
        return initial_state_form

def get_df_for_reporting_allocations(interface:abstractInterface) -> pd.DataFrame:
    event = get_event_from_state(interface)
    display_full_names = interface.get_persistent_value(SHOW_FULL_NAMES)
    include_unallocated_cadets = interface.get_persistent_value(INCLUDE_UNALLOCATED_CADETS)
    df = get_df_for_reporting_allocations_with_flags(event = event, include_unallocated_cadets=include_unallocated_cadets, display_full_names=display_full_names)

    return df


"""
def get_dict_of_arrangements_and_descriptions():
    return dict(
        [
            (arrangement, describe_arrangement(arrangement))
            for arrangement in POSSIBLE_ARRANGEMENTS
        ]
    )
"""



"""

"""
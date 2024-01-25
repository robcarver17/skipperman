from typing import Union

import pandas as pd

from app.logic.abstract_logic_api import initial_state_form
from app.objects.abstract_objects.abstract_form import Form, NewForm, File
from app.objects.abstract_objects.abstract_tables import Table
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.abstract_interface import abstractInterface

from app.logic.forms.reorder_form import reorder_table, reorderFormInterface, list_of_button_names_given_group_order
from app.logic.forms.reorder_matrix import reorder_matrix, reorderMatrixInterface, list_of_button_values_given_list_of_entries

from app.logic.reporting.options.arrangements import save_arrangement, \
    modify_arrangement_given_change_in_group_order, get_arrangement_of_rows_from_storage_or_derive_from_method, \
    modify_arrangement_options_given_custom_list, augment_order_of_groups_with_sizes, get_reporting_options
from app.logic.reporting.options.group_order import save_group_order_to_storage

from app.reporting.arrangement.arrange_options import dict_of_arrangements_that_reorder
from app.reporting.options_and_parameters.report_type_specific_parameters import SpecificParametersForTypeOfReport
from app.reporting.options_and_parameters.report_options import ReportingOptions

def form_for_group_arrangement_options(interface: abstractInterface, specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport, df: pd.DataFrame) -> ListOfLines:

    reporting_options = get_reporting_options(interface=interface,
                                              specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
                                              df=df)
    reorder_list_form = get_reorder_list_of_groups_form_element(reporting_options)
    auto_layout_buttons = get_auto_layout_buttons_form_element()
    reorder_matrix_form = get_reorder_matrix_form_element(interface=interface, reporting_options=reporting_options)

    return \
        ListOfLines(
            [
                "Change order of groups then choose auto-layout option:",
                _______________,
                reorder_list_form,
                _______________,
                auto_layout_buttons,
                _______________,
                _______________,
                "Manually modify layout (number in bracket shows size of group):",
                _______________,
                reorder_matrix_form,
                _______________,
            ]
        )



def get_reorder_list_of_groups_form_element(
                                            reporting_options: ReportingOptions) -> Table:

    group_order = reporting_options.group_order
    reorder_list_form = reorder_table(
        starting_list=group_order,
    )

    return reorder_list_form

def get_auto_layout_buttons_form_element() -> Line:
    auto_layout_buttons = Line(
        ["Click to auto-layout based on group order above"]
        + [
            Button(arrangement_description)
            for arrangement_description in dict_of_arrangements_that_reorder.keys()
        ]
    )
    return auto_layout_buttons


def get_reorder_matrix_form_element(interface: abstractInterface, reporting_options: ReportingOptions) -> Table:
    arrangement_of_rows = get_arrangement_of_rows_from_storage_or_derive_from_method(
        reporting_options=reporting_options,
        interface=interface
    )
    order_of_groups_with_numbers = augment_order_of_groups_with_sizes(
        reporting_options
    )
    reorder_matrix_table = reorder_matrix(
        current_list_of_entries=order_of_groups_with_numbers,
        arrangement_of_rows=arrangement_of_rows,
    )

    return reorder_matrix_table


def post_form_for_group_arrangement_options(
    interface: abstractInterface,
    current_form_name: str,
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
    df: pd.DataFrame

) -> Union[NewForm, Form, File]:

    reporting_options = get_reporting_options(interface=interface,
                                              specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
                                              df=df)

    last_button_pressed = interface.last_button_pressed()
    print("last button %s" % last_button_pressed)

    list_of_arrangement_descriptions_on_buttons = list(dict_of_arrangements_that_reorder.keys())
    list_of_buttons_for_changing_group_order = get_list_of_buttons_changing_group_order(reporting_options)
    list_of_buttons_changing_matrix_shape = get_list_of_buttons_changing_matrix_shape(reporting_options=reporting_options)

    if last_button_pressed in list_of_arrangement_descriptions_on_buttons:
        return change_arrangement_given_method_and_current_order_save_and_return_form_again(interface=interface, current_form_name=current_form_name,reporting_options=reporting_options)

    elif last_button_pressed in list_of_buttons_for_changing_group_order:
        return change_group_order_and_arrangement_save_and_return_form_again(interface=interface,current_form_name=current_form_name,
                                                                             reporting_options=reporting_options)

    elif last_button_pressed in list_of_buttons_changing_matrix_shape:
        return change_arrangement_matrix_save_and_return_form_again(interface=interface, current_form_name=current_form_name,
                                                                    reporting_options=reporting_options)

    else:
        interface.log_error("Button %s not recognised" % last_button_pressed)
        return initial_state_form


def change_arrangement_given_method_and_current_order_save_and_return_form_again(interface: abstractInterface, current_form_name: str,
                                                                                 reporting_options: ReportingOptions) -> NewForm:
    arrangment_method_name = interface.last_button_pressed()
    arrangement_options = reporting_options.arrangement
    print("new arrangement %s" % arrangment_method_name)
    arrangement_options.change_arrangement_options_given_new_method_name(arrangment_method_name=arrangment_method_name)
    print("Arrangement options %s" % arrangement_options)
    save_arrangement(arrangement_options=arrangement_options, interface=interface)

    return NewForm(current_form_name)

def change_group_order_and_arrangement_save_and_return_form_again(interface: abstractInterface, current_form_name: str,
                                                                                 reporting_options: ReportingOptions) -> NewForm:
    ## Change in order of list
    group_order = reporting_options.group_order
    reorder_form_interface = reorderFormInterface(
        interface, current_order=group_order
    )

    ## Need to modify the arrangement as well otherwise things will change when not required to
    indices_to_swap = reorder_form_interface.indices_to_swap()
    modify_arrangement_given_change_in_group_order(interface=interface, indices_to_swap=indices_to_swap)

    new_order = reorder_form_interface.new_order_of_list()
    save_group_order_to_storage(interface=interface, groups_in_order=new_order)

    return NewForm(current_form_name)

def change_arrangement_matrix_save_and_return_form_again(interface: abstractInterface, current_form_name: str,
                                                                                 reporting_options: ReportingOptions) -> NewForm:
    ## Matrix update

    reorder_matrix_interface= get_order_matrix_interface(interface=interface, reporting_options=reporting_options)
    new_arrangement_of_columns = reorder_matrix_interface.new_arrangement()
    modify_arrangement_options_given_custom_list(interface=interface, new_arrangement_of_columns=new_arrangement_of_columns)

    return NewForm(current_form_name)

def get_order_matrix_interface(interface: abstractInterface,reporting_options: ReportingOptions) -> reorderMatrixInterface:
    arrangement_options = reporting_options.arrangement

    order_of_groups_with_numbers = augment_order_of_groups_with_sizes(
        reporting_options=reporting_options
    )

    reorder_matrix_interface = reorderMatrixInterface(
        interface=interface,
        current_arrangement_of_columns=arrangement_options.arrangement_of_columns,
        current_list_of_entries=order_of_groups_with_numbers,
    )

    return reorder_matrix_interface


def get_list_of_buttons_changing_group_order(reporting_options: ReportingOptions):

    return list_of_button_names_given_group_order(reporting_options.group_order)

def get_list_of_buttons_changing_matrix_shape(reporting_options: ReportingOptions) -> list:
    order_of_groups_with_numbers = augment_order_of_groups_with_sizes(
        reporting_options
    )

    return list_of_button_values_given_list_of_entries(order_of_groups_with_numbers)

from typing import Union, Callable, Dict, List

import pandas as pd

from app.backend.reporting.arrangement.arrange_options import dict_of_arrangements_that_reorder
from app.backend.reporting.options_and_parameters.report_options import ReportingOptions
from app.backend.reporting.options_and_parameters.report_type_specific_parameters import \
    SpecificParametersForTypeOfReport
from app.objects.abstract_objects.abstract_text import bold

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_form import Form, NewForm, File
from app.objects.abstract_objects.abstract_tables import Table
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.frontend.forms.reorder_form import (
    reorder_table,
    reorderFormInterface,
    list_of_button_names_given_group_order,
)
from app.frontend.forms.reorder_matrix import (
    reorder_matrix,
    reorderMatrixInterface,
    list_of_button_values_given_list_of_entries,
)

from app.frontend.reporting.shared.arrangements import (
    get_arrangement_of_rows_from_storage_or_derive_from_method,
    get_arrangement_of_columns_from_storage_or_derive_from_method,
    modify_arrangement_options_and_group_order_to_reflect_arrangement_method_name,
    modify_arrangement_given_change_in_group_order,
    remove_empty_groups_from_group_order_and_arrangement,
    add_groups_to_group_order_and_arrangement,
    modify_arrangement_options_given_custom_list,
)
from app.frontend.reporting.shared.reporting_options import (
    augment_order_of_groups_with_sizes,
    get_reporting_options,
)
from app.backend.reporting.arrangement.get_and_update_arrangement_options import (
    update_arrangement_and_group_order,
)
from app.frontend.reporting.shared.group_order import (
    get_missing_groups,
    get_empty_groups,
)



def form_for_group_arrangement_options(
    interface: abstractInterface,
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
    dict_of_df: Dict[str, pd.DataFrame],
) -> ListOfLines:
    reporting_options = get_reporting_options(
        interface=interface,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
        dict_of_df=dict_of_df,
    )

    add_delete_buttons = get_add_delete_buttons_for_group_ordering(reporting_options)
    reorder_list_form = get_reorder_list_of_groups_form_element(reporting_options)
    auto_layout_buttons = get_auto_layout_buttons_form_element()
    reorder_matrix_form = get_reorder_matrix_form_element(
        interface=interface, reporting_options=reporting_options
    )
    missing_and_empty_lines = flag_missing_and_empty_groups(
         reporting_options=reporting_options
    )

    return ListOfLines(missing_and_empty_lines+
        [
            add_delete_buttons,
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


def flag_missing_and_empty_groups(
   reporting_options: ReportingOptions
) -> List[Line]:
    missing_groups = flag_missing_groups(reporting_options)
    empty_groups = flag_empty_groups(reporting_options)

    return [missing_groups, empty_groups]

def flag_missing_groups(
   reporting_options: ReportingOptions
) -> Line:
    missing_groups = get_missing_groups(reporting_options=reporting_options)

    if len(missing_groups) == 0:
        missing_line = ""
    else:
        order_of_missing_groups_as_text = ", ".join(missing_groups)
        warning = (
            "FOLLOWING REPORTING GROUPS ARE IN DATA, BUT MISSING FROM REPORT CONFIGURATION: %s (Will be excluded from report unless added)"
            % order_of_missing_groups_as_text
        )
        missing_line = Line(bold(warning))


    return missing_line


def flag_empty_groups(
   reporting_options: ReportingOptions
) -> Line:
    empty_groups = get_empty_groups(reporting_options)

    if len(empty_groups) == 0:
        empty_line = ""
    else:
        order_of_empty_groups_as_text = ", ".join(empty_groups)
        warning = (
            "These reporting groups are in the reporting configuration, but empty in the reporting data: %s (Will be excluded from report - optionally remove to make arrangement easier)"
            % order_of_empty_groups_as_text
        )
        empty_line = Line(warning)

    return empty_line


def get_reorder_list_of_groups_form_element(
    reporting_options: ReportingOptions,
) -> Table:
    group_order = reporting_options.group_order
    reorder_list_form = reorder_table(starting_list=group_order, include_delete=True)

    return reorder_list_form


def get_add_delete_buttons_for_group_ordering(
    reporting_options: ReportingOptions,
) -> Line:
    missing_groups = get_missing_groups(reporting_options)
    empty_groups = get_empty_groups(reporting_options)

    if len(missing_groups) > 0:
        if len(missing_groups)>3:
            missing_text = "Add %d missing groups to report" % len(missing_groups)
        else:
            missing_text = "Add the following missing groups to report: %s" % ", ".join(missing_groups)
        missing_groups_button = Button(
            missing_text,
            value=ADD_MISSING_BUTTON_NAME,
        )
    else:
        missing_groups_button = ""

    if len(empty_groups) > 0:
        if len(empty_groups)>3:
            empty_text = "Remove %d empty groups from report" % len(empty_groups)
        else:
            empty_text =             "Remove the following empty groups from report: %s" % ", ".join(empty_groups)
        empty_groups_button = Button(
            empty_text,
            value=REMOVE_EMPTY_BUTTON_NAME,
        )
    else:
        empty_groups_button = ""

    return Line([missing_groups_button, empty_groups_button])


def get_auto_layout_buttons_form_element() -> Line:
    auto_layout_buttons = Line(
        ["Click to auto-layout based on group order above:  "]
        + [
            Button(arrangement_description)
            for arrangement_description in dict_of_arrangements_that_reorder.keys()
        ]
    )
    return auto_layout_buttons


def get_reorder_matrix_form_element(
    interface: abstractInterface, reporting_options: ReportingOptions
) -> Table:
    arrangement_of_rows = get_arrangement_of_rows_from_storage_or_derive_from_method(
        reporting_options=reporting_options, object_store=interface.object_store
    )
    order_of_groups_with_numbers = augment_order_of_groups_with_sizes(reporting_options)
    reorder_matrix_table = reorder_matrix(
        current_list_of_entries=order_of_groups_with_numbers,
        arrangement_of_rows=arrangement_of_rows,
    )

    return reorder_matrix_table


def post_form_for_group_arrangement_options(
    interface: abstractInterface,
    current_form_function: Callable,
    specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport,
    dict_of_df: Dict[str, pd.DataFrame],
) -> Union[NewForm, Form, File]:
    reporting_options = get_reporting_options(
        interface=interface,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
        dict_of_df=dict_of_df,
    )

    list_of_arrangement_descriptions_on_buttons = list(
        dict_of_arrangements_that_reorder.keys()
    )
    list_of_buttons_for_changing_group_order = get_list_of_buttons_changing_group_order(
        reporting_options
    )
    list_of_buttons_changing_matrix_shape = get_list_of_buttons_changing_matrix_shape(
        reporting_options=reporting_options
    )

    last_button_pressed = interface.last_button_pressed()

    if last_button_pressed in list_of_arrangement_descriptions_on_buttons:
        change_arrangement_given_method_and_current_order(
            interface=interface, reporting_options=reporting_options
        )

    elif last_button_pressed == REMOVE_EMPTY_BUTTON_NAME:
        remove_empty_from_group_order_and_arrangement(
            interface=interface, reporting_options=reporting_options
        )

    elif last_button_pressed == ADD_MISSING_BUTTON_NAME:
        add_missing_to_group_order_and_arrangement(
            interface=interface, reporting_options=reporting_options
        )

    elif last_button_pressed in list_of_buttons_for_changing_group_order:
        change_group_order_and_arrangement(
            interface=interface, reporting_options=reporting_options
        )

    elif last_button_pressed in list_of_buttons_changing_matrix_shape:
        change_arrangement_matrix(
            interface=interface, reporting_options=reporting_options
        )

    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()

    return interface.get_new_form_given_function(current_form_function)


def change_arrangement_given_method_and_current_order(
    interface: abstractInterface, reporting_options: ReportingOptions
):
    arrangement_method_name = interface.last_button_pressed()
    arrange_options_and_group_order = (
        modify_arrangement_options_and_group_order_to_reflect_arrangement_method_name(
            reporting_options=reporting_options,
            arrangement_method_name=arrangement_method_name,
        )
    )

    update_arrangement_and_group_order(
        arrangement_and_group_options=arrange_options_and_group_order,
        object_store=interface.object_store,
        report_type=reporting_options.specific_parameters.report_type,
    )


def change_group_order_and_arrangement(
    interface: abstractInterface, reporting_options: ReportingOptions
):
    ## Change in order of list
    group_order = reporting_options.group_order
    reorder_form_interface = reorderFormInterface(interface, current_order=group_order)

    ## Need to modify the arrangement as well otherwise things will change when not required to
    indices_to_swap = reorder_form_interface.indices_to_swap()
    new_group_order = reorder_form_interface.new_order_of_list()
    modify_arrangement_given_change_in_group_order(
        object_store=interface.object_store,
        indices_to_swap=indices_to_swap,
        new_group_order=new_group_order,
        report_type=reporting_options.specific_parameters.report_type,
    )


def remove_empty_from_group_order_and_arrangement(
    interface: abstractInterface, reporting_options: ReportingOptions
):
    empty_groups = get_empty_groups(reporting_options)
    remove_empty_groups_from_group_order_and_arrangement(
        object_store=interface.object_store,
        empty_groups=empty_groups,
        reporting_options=reporting_options,
    )


def add_missing_to_group_order_and_arrangement(
    interface: abstractInterface, reporting_options: ReportingOptions
):
    missing_groups = get_missing_groups(reporting_options)
    add_groups_to_group_order_and_arrangement(interface=interface, list_of_groups_to_add=missing_groups,
                                              reporting_options=reporting_options)


def change_arrangement_matrix(
    interface: abstractInterface, reporting_options: ReportingOptions
):
    ## Matrix update

    reorder_matrix_interface = get_order_matrix_interface(
        interface=interface, reporting_options=reporting_options
    )
    new_arrangement_of_columns = reorder_matrix_interface.new_arrangement()
    modify_arrangement_options_given_custom_list(
        interface=interface,
        new_arrangement_of_columns=new_arrangement_of_columns,
        report_type=reporting_options.specific_parameters.report_type,
    )


def get_order_matrix_interface(
    interface: abstractInterface, reporting_options: ReportingOptions
) -> reorderMatrixInterface:
    arrangement_of_columns = (
        get_arrangement_of_columns_from_storage_or_derive_from_method(
            object_store=interface.object_store, reporting_options=reporting_options
        )
    )

    order_of_groups_with_numbers = augment_order_of_groups_with_sizes(
        reporting_options=reporting_options
    )

    reorder_matrix_interface = reorderMatrixInterface(
        interface=interface,
        current_arrangement_of_columns=arrangement_of_columns,
        current_list_of_entries=order_of_groups_with_numbers,
    )

    return reorder_matrix_interface


def get_list_of_buttons_changing_group_order(reporting_options: ReportingOptions):
    return list_of_button_names_given_group_order(reporting_options.group_order)


def get_list_of_buttons_changing_matrix_shape(
    reporting_options: ReportingOptions,
) -> list:
    order_of_groups_with_numbers = augment_order_of_groups_with_sizes(reporting_options)

    return list_of_button_values_given_list_of_entries(order_of_groups_with_numbers)


ADD_MISSING_BUTTON_NAME = "addMissing"
REMOVE_EMPTY_BUTTON_NAME = "removeEmpty"

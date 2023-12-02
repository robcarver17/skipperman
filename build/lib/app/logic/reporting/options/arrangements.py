import pandas as pd

from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.logic.reporting.options.group_order import get_group_order_from_stored_or_df
from app.logic.reporting.options.print_options import get_saved_print_options
from app.logic.reporting.constants import (
    ARRANGE_GROUP_LAYOUT_METHOD,
    ARRANGE_GROUP_LAYOUT_ORDER, )

from app.objects.constants import missing_data

from app.reporting.arrangement.arrange_options import ArrangeGroupsOptions
from app.reporting.arrangement.arrangement_methods import (
    DEFAULT_ARRANGEMENT_NAME,
    ArrangementMethod,
)
from app.reporting.arrangement.arrangement_order import ArrangementOfColumns, ArrangementOfRows

from app.reporting.options_and_parameters.report_type_specific_parameters import SpecificParametersForTypeOfReport
from app.reporting.options_and_parameters.report_options import ReportingOptions
from app.reporting.options_and_parameters.marked_up_list_from_df_parameters import \
    create_parameters_to_create_marked_up_list_from_df

from app.reporting.process_stages.create_list_of_columns_from_groups import \
    create_arrangement_from_list_of_groups_of_marked_up_str
from app.reporting.process_stages.create_list_of_groups_from_df import create_list_of_group_of_marked_up_str_from_df, \
    get_grouped_df


def get_stored_arrangement(interface: abstractInterface) -> ArrangeGroupsOptions:
    arrangement_method_as_str = interface.get_persistent_value(
        ARRANGE_GROUP_LAYOUT_METHOD
    )
    if arrangement_method_as_str is missing_data:
        arrangement_method_as_str = DEFAULT_ARRANGEMENT_NAME
        interface.set_persistent_value(
            ARRANGE_GROUP_LAYOUT_METHOD, arrangement_method_as_str
        )
    arrangement_method = ArrangementMethod[arrangement_method_as_str]

    arrangement_order_as_list = interface.get_persistent_value(
        ARRANGE_GROUP_LAYOUT_ORDER
    )
    if arrangement_order_as_list is missing_data:
        ## Don't bother storing, happy to pick up empty list next time
        arrangement_order = ArrangementOfColumns()
    else:
        arrangement_order = ArrangementOfColumns(arrangement_order_as_list)

    return ArrangeGroupsOptions(
        arrangement_method=arrangement_method,
        arrangement_of_columns=arrangement_order,
    )


def save_arrangement(
    interface: abstractInterface, arrangement_options: ArrangeGroupsOptions
):
    print("Saving arrangement %s" % str(arrangement_options))
    arrangement_method_as_str = arrangement_options.arrangement_method.name
    interface.set_persistent_value(
        ARRANGE_GROUP_LAYOUT_METHOD, arrangement_method_as_str
    )

    arrangement_order_as_list = list(arrangement_options.arrangement_of_columns)
    interface.set_persistent_value(
        ARRANGE_GROUP_LAYOUT_ORDER, arrangement_order_as_list
    )


def modify_arrangement_given_change_in_group_order(interface: abstractInterface, indices_to_swap: tuple):
    ## Need to modify the indices in the matrix layout or that will change when should not
    arrangement_options = get_stored_arrangement(interface)
    print("Arrangement was %s" % str(arrangement_options))
    arrangement_options.arrangement_of_columns.swap_indices(indices_to_swap)
    save_arrangement(arrangement_options=arrangement_options, interface=interface)
    print("Arrangement is %s" % str(arrangement_options))

def modify_arrangement_options_given_custom_list(interface: abstractInterface, new_arrangement_of_columns: ArrangementOfColumns):
    arrangement_options = get_stored_arrangement(interface)
    ## will change method to custom
    arrangement_options.add_arrangement_of_columns(new_arrangement_of_columns)
    save_arrangement(arrangement_options=arrangement_options, interface=interface)

def get_arrangement_of_rows_from_storage_or_derive_from_method(interface: abstractInterface, reporting_options: ReportingOptions) -> ArrangementOfRows:
    arrangement_of_columns = get_arrangement_of_columns_from_storage_or_derive_from_method(
        interface,reporting_options=reporting_options
    )
    arrangement_of_rows = arrangement_of_columns.transpose_to_rows()

    return arrangement_of_rows


def get_arrangement_of_columns_from_storage_or_derive_from_method(interface: abstractInterface, reporting_options: ReportingOptions) -> ArrangementOfColumns:
    arrangement_options = reporting_options.arrangement

    if arrangement_options.no_arrangement_of_columns_provided:
        print("No arrangement provided creating one")
        ## create an arrangement using the current algo
        arrangement_of_columns = create_arrangement_from_order_and_algo_and_save(
            interface=interface, reporting_options=reporting_options
        )
    else:
        print("Using stored column arrangement %s" % str(arrangement_options.arrangement_of_columns))
        arrangement_of_columns = arrangement_options.arrangement_of_columns

    return arrangement_of_columns



def create_arrangement_from_order_and_algo_and_save(
    interface: abstractInterface,
    reporting_options: ReportingOptions,
) -> ArrangementOfColumns:

    arrangement_of_columns = create_arrangement_from_order_and_algo(reporting_options=reporting_options)
    print("Following arrangement created from algo: %s" % str(arrangement_of_columns))

    arrangement_options = reporting_options.arrangement
    arrangement_options.add_arrangement_of_columns(arrangement_of_columns)
    print("Options now are %s" % str(arrangement_options))
    save_arrangement(interface=interface, arrangement_options=arrangement_options)

    return arrangement_of_columns

def create_arrangement_from_order_and_algo(
    reporting_options: ReportingOptions,
) -> ArrangementOfColumns:

    list_of_groups_of_marked_up_str = create_list_of_group_of_marked_up_str_from_df(
        df=reporting_options.df,
        marked_up_list_from_df_parameters=reporting_options.marked_up_list_from_df_parameters,
    )

    arrangement_of_columns = create_arrangement_from_list_of_groups_of_marked_up_str(
        list_of_groups_of_marked_up_str=list_of_groups_of_marked_up_str,
        reporting_options=reporting_options
    )

    return arrangement_of_columns


def augment_order_of_groups_with_sizes(
    reporting_options: ReportingOptions
) -> list:

    grouped_df = get_grouped_df(
        df=reporting_options.df,
        marked_up_list_from_df_parameters=reporting_options.marked_up_list_from_df_parameters,
    )

    sizes = grouped_df.size()

    return ["%s (%d)" % (group, sizes[group]) for group in reporting_options.group_order]


def get_reporting_options(interface: abstractInterface, specific_parameters_for_type_of_report: SpecificParametersForTypeOfReport, df: pd.DataFrame) -> ReportingOptions:
    group_order = get_group_order_from_stored_or_df(
        interface=interface,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
        df=df,
    )
    arrangement_options = get_stored_arrangement(interface)
    print_options = get_saved_print_options(interface=interface, report_type=specific_parameters_for_type_of_report.report_type)

    marked_up_list_from_df_parameters_with_actual_group_order = create_parameters_to_create_marked_up_list_from_df(
        print_options=print_options,
        specific_parameters=specific_parameters_for_type_of_report,
        group_order=group_order
    )

    return ReportingOptions(arrangement=arrangement_options,
                            group_order=group_order,
                            specific_parameters=specific_parameters_for_type_of_report,
                            df=df,
                            print_options=print_options,
                            marked_up_list_from_df_parameters=marked_up_list_from_df_parameters_with_actual_group_order)

from app.backend.reporting.arrangement.arrange_options import ArrangementOptionsAndGroupOrder
from app.backend.reporting.arrangement.group_order import GroupOrder
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.reporting.shared.arrangement_state import save_arrangement_and_group_order, \
    get_stored_arrangement_and_group_order

from app.backend.reporting.arrangement.arrangement_order import ArrangementOfColumns, ArrangementOfRows, \
    ListOfArrangementOfColumns, IndicesToSwap

from app.backend.reporting.options_and_parameters.report_options import ReportingOptions


from app.backend.reporting.process_stages.create_list_of_columns_from_groups import \
    create_arrangement_from_list_of_pages
from app.backend.reporting.process_stages.create_list_of_groups_from_df import create_list_of_pages_from_dict_of_df


def get_arrangement_of_rows_from_storage_or_derive_from_method(interface: abstractInterface, reporting_options: ReportingOptions) -> ArrangementOfRows:
    arrangement_of_columns = get_arrangement_of_columns_from_storage_or_derive_from_method(
        interface,reporting_options=reporting_options
    )
    arrangement_of_rows = arrangement_of_columns.transpose_to_rows()

    return arrangement_of_rows


def get_arrangement_of_columns_from_storage_or_derive_from_method(interface: abstractInterface, reporting_options: ReportingOptions) -> ArrangementOfColumns:
    arrangement_options = reporting_options.arrangement

    if arrangement_options.no_arrangement_of_columns_provided():
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
    arrangement_options = reporting_options.arrangement
    arrangement_options.add_arrangement_of_columns(arrangement_of_columns)
    save_arrangement_and_group_order(interface=interface, arrangement_and_group_options=reporting_options.arrange_options_and_group_order,
                                     report_type=reporting_options.specific_parameters.report_type)

    return arrangement_of_columns

def create_arrangement_from_order_and_algo(
    reporting_options: ReportingOptions,
) -> ArrangementOfColumns:

    list_of_pages = create_list_of_pages_from_dict_of_df(
        dict_of_df=reporting_options.dict_of_df,
        marked_up_list_from_df_parameters=reporting_options.marked_up_list_from_df_parameters,
    )
    list_of_arrangement_of_columns = create_arrangement_from_list_of_pages(list_of_pages=list_of_pages,
                                                                   reporting_options=reporting_options)

    print("list of arrangement of columns %s" % str(list_of_arrangement_of_columns))
    arrangement_of_columns = from_list_of_arrangement_of_columns_to_typical_arrangement_of_columns(list_of_arrangement_of_columns)

    print("Arrange of columns %s" % str(arrangement_of_columns))
    return arrangement_of_columns

def from_list_of_arrangement_of_columns_to_typical_arrangement_of_columns(list_of_arrangement_of_columns: ListOfArrangementOfColumns) -> ArrangementOfColumns:
    ## FIXME TEMP
    return list_of_arrangement_of_columns[0]


def modify_arrangement_options_and_group_order_to_reflect_arrangement_method_name(reporting_options: ReportingOptions,
                                                                                  arrangement_method_name: str) -> ArrangementOptionsAndGroupOrder:
    arrangement_options_and_group_order = reporting_options.arrange_options_and_group_order
    arrangement_options_and_group_order.arrangement_options.change_arrangement_options_given_new_method_name(arrangement_method_name)

    ## above modifies arrangement method inside reporting options, we now replace the columns
    new_arrangement_of_columns = create_arrangement_from_order_and_algo(reporting_options=reporting_options)
    arrangement_options_and_group_order.replace_column_arrangement(new_arrangement_of_columns)

    return arrangement_options_and_group_order


def modify_arrangement_given_change_in_group_order(interface: abstractInterface, report_type: str,
                                                   indices_to_swap: IndicesToSwap, new_group_order: GroupOrder):
    ## Need to modify the indices in the matrix layout or that will change when should not
    arrangement_options_and_group_order = get_stored_arrangement_and_group_order(interface, report_type=report_type)
    arrangement_options_and_group_order.arrangement_options.arrangement_of_columns.swap_or_delete_indices(indices_to_swap)
    arrangement_options_and_group_order.group_order = new_group_order

    save_arrangement_and_group_order(arrangement_and_group_options=arrangement_options_and_group_order, interface=interface, report_type=report_type)


def  remove_empty_groups_from_group_order_and_arrangement(interface: abstractInterface ,empty_groups: GroupOrder,  reporting_options: ReportingOptions):
    arrangement_options_and_group_order = get_stored_arrangement_and_group_order(interface, report_type=reporting_options.specific_parameters.report_type)
    arrangement_options_and_group_order.remove_empty_groups_from_group_order_and_arrangement(empty_groups)
    arrangement_options_and_group_order.reset_arrangement_back_to_default()

    ## above modifies arrangement method inside reporting options, we now replace the columns
    new_arrangement_of_columns = create_arrangement_from_order_and_algo(reporting_options=reporting_options)
    arrangement_options_and_group_order.replace_column_arrangement(new_arrangement_of_columns)
    reset_arrangement_and_regenerate_columns(reporting_options=reporting_options, arrangement_options_and_group_order=arrangement_options_and_group_order)

    save_arrangement_and_group_order(arrangement_and_group_options=arrangement_options_and_group_order, interface=interface, report_type=reporting_options.specific_parameters.report_type)


def  add_missing_groups_to_group_order_and_arrangement(interface: abstractInterface ,missing_groups: GroupOrder,  reporting_options: ReportingOptions):
    arrangement_options_and_group_order = get_stored_arrangement_and_group_order(interface, report_type=reporting_options.specific_parameters.report_type)
    arrangement_options_and_group_order.add_missing_groups_to_group_order_and_arrangement(missing_groups=missing_groups)
    reset_arrangement_and_regenerate_columns(reporting_options=reporting_options, arrangement_options_and_group_order=arrangement_options_and_group_order)
    save_arrangement_and_group_order(arrangement_and_group_options=arrangement_options_and_group_order, interface=interface, report_type=reporting_options.specific_parameters.report_type)


def reset_arrangement_and_regenerate_columns(reporting_options: ReportingOptions, arrangement_options_and_group_order: ArrangementOptionsAndGroupOrder):
    arrangement_options_and_group_order.reset_arrangement_back_to_default()

    ## above modifies arrangement method inside reporting options, we now replace the columns
    new_arrangement_of_columns = create_arrangement_from_order_and_algo(reporting_options=reporting_options)
    arrangement_options_and_group_order.replace_column_arrangement(new_arrangement_of_columns)


def modify_arrangement_options_given_custom_list(interface: abstractInterface, report_type: str, new_arrangement_of_columns: ArrangementOfColumns):
    arrangement_options_and_group_order = get_stored_arrangement_and_group_order(interface=interface, report_type=report_type)
    ## will change method to custom
    arrangement_options_and_group_order.arrangement_options.add_arrangement_of_columns(new_arrangement_of_columns)
    save_arrangement_and_group_order(arrangement_and_group_options=arrangement_options_and_group_order, interface=interface, report_type=report_type)

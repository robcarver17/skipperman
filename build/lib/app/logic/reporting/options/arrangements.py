from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.reporting.options.arrangement_state import save_arrangement

from app.backend.reporting.arrangement.arrangement_order import ArrangementOfColumns, ArrangementOfRows, \
    ListOfArrangementOfColumns

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
    save_arrangement(interface=interface, arrangement_options=arrangement_options)

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

    arrangement_of_columns = from_list_of_arrangement_of_columns_to_typical_arrangement_of_columns(list_of_arrangement_of_columns)

    return arrangement_of_columns

def from_list_of_arrangement_of_columns_to_typical_arrangement_of_columns(list_of_arrangement_of_columns: ListOfArrangementOfColumns) -> ArrangementOfColumns:
    ## FIXME TEMP
    return list_of_arrangement_of_columns[0]


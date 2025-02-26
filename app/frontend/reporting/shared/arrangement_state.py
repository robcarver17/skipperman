from app.backend.reporting.arrangement.group_order import get_group_order_from_dict_of_df_given_report_parameters
from app.frontend.reporting.shared.arrangements import load_reset_and_update_arrangement_to_groups_in_data
from app.backend.reporting.report_generator import ReportGenerator
from app.frontend.reporting.shared.reporting_options import get_reporting_options
from app.objects.abstract_objects.abstract_interface import abstractInterface


def reset_arrangement_to_default_with_groups_in_data(interface: abstractInterface, report_generator: ReportGenerator):
    ## Need to have updated specific parameters first
    specific_parameters_for_type_of_report = report_generator.specific_parameters_for_type_of_report
    dict_of_df = report_generator.get_dict_of_df(interface)

    reporting_options = get_reporting_options(
        interface=interface,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
        dict_of_df=dict_of_df,
    )

    group_order_from_df = get_group_order_from_dict_of_df_given_report_parameters(
        dict_of_df=dict_of_df,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
    ) ## will this include unallocated?

    load_reset_and_update_arrangement_to_groups_in_data(interface=interface, reporting_options=reporting_options, ordered_groups_in_data=group_order_from_df)

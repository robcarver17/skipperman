import os

from app.backend.file_handling import generate_qr_code_for_file_in_public_path
from app.backend.reporting.options_and_parameters.print_options import PrintOptions
from app.backend.reporting.process_stages.create_column_report_from_df import (
    create_column_report_from_df_and_return_filename,
)
from app.backend.reporting.process_stages.create_file_from_list_of_columns import \
    get_download_path_and_filename_for_report
from app.backend.reporting.report_generator import ReportGenerator
from app.frontend.reporting.shared.reporting_options import get_reporting_options
from app.objects.abstract_objects.abstract_form import File
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.utilities.exceptions import arg_not_passed


def qr_code_for_report(interface: abstractInterface, report_generator: ReportGenerator):
    print_options = get_print_options_without_override(interface=interface, report_generator=report_generator)
    path_and_filename = get_download_path_and_filename_for_report(print_options)

    return generate_qr_code_for_file_in_public_path(filename_without_extension=path_and_filename.filename_without_extension)


def create_generic_report(
    interface: abstractInterface,
    report_generator: ReportGenerator,
    override_print_options: dict = arg_not_passed,
    ignore_stored_print_option_values_and_use_default: bool = False,
override_additional_options:dict = arg_not_passed
) -> File:

    filename = create_generic_report_and_return_filename(
        interface,
        report_generator=report_generator,
        override_print_options=override_print_options,
        override_additional_options=override_additional_options,
        ignore_stored_print_option_values_and_use_default=ignore_stored_print_option_values_and_use_default
    )
    return File(filename)


def create_generic_report_and_return_filename(
    interface: abstractInterface,
    report_generator: ReportGenerator,
    override_print_options: dict = arg_not_passed,
override_additional_options:dict = arg_not_passed,
        ignore_stored_print_option_values_and_use_default: bool = False,

) -> str:
    print("Creating report")

    specific_parameters_for_type_of_report = (
        report_generator.specific_parameters_for_type_of_report
    )

    dict_of_df = report_generator.get_dict_of_df(interface,
                                                     override_additional_options=override_additional_options)

    reporting_options = get_reporting_options(
        interface=interface,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
        dict_of_df=dict_of_df,
        override_print_options=override_print_options,
        ignore_stored_print_option_values_and_use_default=ignore_stored_print_option_values_and_use_default

    )

    reporting_options.filter_arrangement_options_in_place_to_remove_non_existent_groups()

    filename = create_column_report_from_df_and_return_filename(
        reporting_options=reporting_options
    )

    return filename

def get_print_options_without_override(interface: abstractInterface, report_generator: ReportGenerator) -> PrintOptions:

    specific_parameters_for_type_of_report = (
        report_generator.specific_parameters_for_type_of_report
    )

    dict_of_df = report_generator.get_dict_of_df(interface)

    reporting_options = get_reporting_options(
        interface=interface,
        specific_parameters_for_type_of_report=specific_parameters_for_type_of_report,
        dict_of_df=dict_of_df,

    )

    return reporting_options.print_options
